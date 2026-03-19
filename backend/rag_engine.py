"""RAG 검색 엔진 - Vector + Graph 하이브리드 검색 및 LLM 스트리밍."""

import json
import logging
from collections import defaultdict
from typing import AsyncGenerator

from openai import OpenAI
from pydantic import BaseModel

from shared.config import (
    GRAPH_SEARCH_TOP_K,
    OPENAI_API_BASE,
    OPENAI_API_KEY,
    OPENAI_CHAT_MODEL,
    VECTOR_SEARCH_TOP_K,
)
from shared.db import ChromaRepository, KuzuRepository
from shared.embeddings import embed_text

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """당신은 사내 지식 문서를 기반으로 답변하는 AI 어시스턴트입니다.
제공된 컨텍스트를 기반으로 정확하게 답변하세요.
컨텍스트에 없는 내용은 "제공된 문서에서 관련 정보를 찾을 수 없습니다"라고 답변하세요.
답변 시 참조한 문서가 있다면 자연스럽게 언급해주세요."""


class Source(BaseModel):
    file_name: str
    excerpt: str


class RAGEngine:
    def __init__(self):
        self._chroma = ChromaRepository()
        self._graph = KuzuRepository()
        self._llm = OpenAI(base_url=OPENAI_API_BASE, api_key=OPENAI_API_KEY)

    def close(self):
        self._graph.close()

    def search(self, query: str) -> tuple[str, list[Source]]:
        """하이브리드 검색 수행. (context_text, sources) 반환."""
        try:
            # Vector 검색
            query_embedding = embed_text(query)
            vector_results = self._chroma.search(query_embedding, top_k=VECTOR_SEARCH_TOP_K)

            # Graph 검색: 질의에서 엔티티 추출 후 관계 탐색
            entity_names = self._extract_query_entities(query)
            graph_results = []
            if entity_names:
                graph_results = self._graph.search_related(entity_names, top_k=GRAPH_SEARCH_TOP_K)

            # 결과 결합
            context_text, sources = self._merge_results(vector_results, graph_results)
            return context_text, sources

        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return "", []

    def _extract_query_entities(self, query: str) -> list[str]:
        """질의에서 핵심 엔티티명 추출 (LLM 기반)."""
        try:
            response = self._llm.chat.completions.create(
                model=OPENAI_CHAT_MODEL,
                messages=[{
                    "role": "user",
                    "content": f"다음 질문에서 핵심 키워드/엔티티를 JSON 배열로 추출하세요. 최대 5개.\n질문: {query}\n응답 형식: [\"키워드1\", \"키워드2\"]",
                }],
                temperature=0,
            )
            content = response.choices[0].message.content.strip()
            if "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                if content.startswith("json"):
                    content = content[4:].strip()
            return json.loads(content)
        except Exception as e:
            logger.warning(f"엔티티 추출 실패: {e}")
            return []

    def _merge_results(self, vector_results: dict, graph_results: list[dict]) -> tuple[str, list[Source]]:
        """RRF로 Vector + Graph 결과 결합."""
        K = 60
        scores = defaultdict(float)
        chunk_map = {}

        # Vector 결과 스코어링
        if vector_results and vector_results.get("documents"):
            docs = vector_results["documents"][0]
            metas = vector_results["metadatas"][0] if vector_results.get("metadatas") else [{}] * len(docs)
            for rank, (doc, meta) in enumerate(zip(docs, metas)):
                key = f"{meta.get('doc_id', '')}##{meta.get('chunk_index', rank)}"
                scores[key] += 1.0 / (K + rank + 1)
                chunk_map[key] = {"content": doc, "file_name": meta.get("file_name", "unknown"), "doc_id": meta.get("doc_id", "")}

        # Graph 결과를 context에 추가
        graph_context = ""
        if graph_results:
            relations = [f"{r.get('source', '')} --[{r.get('rel_subtype', r.get('rel_type', ''))}]--> {r.get('target', '')}" for r in graph_results]
            graph_context = "\n[관련 지식 그래프]\n" + "\n".join(relations)

        # 스코어 기준 정렬
        sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)

        # Context 구성
        context_parts = []
        source_map = {}
        for key in sorted_keys[:VECTOR_SEARCH_TOP_K]:
            chunk = chunk_map[key]
            context_parts.append(chunk["content"])
            fname = chunk["file_name"]
            if fname not in source_map:
                source_map[fname] = chunk["content"][:200]

        context_text = "\n\n".join(context_parts)
        if graph_context:
            context_text += "\n" + graph_context

        sources = [Source(file_name=fn, excerpt=ex) for fn, ex in source_map.items()]
        return context_text, sources

    async def generate_stream(self, query: str, context: str, history: list[dict]) -> AsyncGenerator[dict, None]:
        """LLM 스트리밍 응답 생성."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            messages.append({"role": "system", "content": f"[참조 문서]\n{context}"})

        # 대화 이력 추가 (최근 20턴)
        for msg in history[-20:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": query})

        try:
            stream = self._llm.chat.completions.create(
                model=OPENAI_CHAT_MODEL,
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield {"event": "token", "data": chunk.choices[0].delta.content}

        except Exception as e:
            logger.error(f"LLM 스트리밍 실패: {e}")
            yield {"event": "error", "data": "응답 생성에 실패했습니다. 다시 시도해주세요."}
