"""RAG 검색 엔진 - Vector + Graph 하이브리드 검색 및 LLM 스트리밍.

검색 흐름:
1. 사용자 질의 → 벡터 임베딩 → ChromaDB 코사인 유사도 검색
2. 사용자 질의 → LLM 엔티티 추출 → KùzuDB 1-hop 관계 탐색
3. RRF(Reciprocal Rank Fusion)로 두 결과를 결합하여 최종 컨텍스트 구성
4. 컨텍스트 + 대화 이력 → LLM 스트리밍 응답
"""

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
            query_embedding = embed_text(query)
            vector_results = self._chroma.search(query_embedding, top_k=VECTOR_SEARCH_TOP_K)

            # Graph 검색: 질의에서 LLM으로 엔티티를 추출한 뒤 관계 탐색
            entity_names = self._extract_query_entities(query)
            graph_results = []
            if entity_names:
                graph_results = self._graph.search_related(entity_names, top_k=GRAPH_SEARCH_TOP_K)

            context_text, sources = self._merge_results(vector_results, graph_results)
            return context_text, sources

        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return "", []

    def _extract_query_entities(self, query: str) -> list[str]:
        """질의에서 핵심 엔티티명을 LLM으로 추출한다.

        Graph 검색의 시작점이 되는 엔티티를 결정하는 단계.
        실패 시 빈 리스트를 반환하여 Vector 검색만으로 동작한다.
        """
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
            # LLM이 마크다운 코드블록으로 감싸는 경우 처리
            if "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                if content.startswith("json"):
                    content = content[4:].strip()
            return json.loads(content)
        except Exception as e:
            logger.warning(f"엔티티 추출 실패: {e}")
            return []

    def _merge_results(self, vector_results: dict, graph_results: list[dict]) -> tuple[str, list[Source]]:
        """RRF(Reciprocal Rank Fusion)로 Vector + Graph 결과를 결합한다.

        RRF 공식: score(d) = Σ 1/(K + rank)
        K=60은 RRF 논문의 권장값으로, 상위 랭크와 하위 랭크 간 점수 차이를 완화한다.
        """
        K = 60
        scores = defaultdict(float)
        chunk_map = {}

        # Vector 결과: 랭크 기반 RRF 스코어 부여
        if vector_results and vector_results.get("documents"):
            docs = vector_results["documents"][0]
            metas = vector_results["metadatas"][0] if vector_results.get("metadatas") else [{}] * len(docs)
            for rank, (doc, meta) in enumerate(zip(docs, metas)):
                key = f"{meta.get('doc_id', '')}##{meta.get('chunk_index', rank)}"
                scores[key] += 1.0 / (K + rank + 1)
                chunk_map[key] = {"content": doc, "file_name": meta.get("file_name", "unknown"), "doc_id": meta.get("doc_id", "")}

        # Graph 결과: 관계를 텍스트로 변환하여 컨텍스트에 추가
        graph_context = ""
        if graph_results:
            relations = [f"{r.get('source', '')} --[{r.get('rel_subtype', r.get('rel_type', ''))}]--> {r.get('target', '')}" for r in graph_results]
            graph_context = "\n[관련 지식 그래프]\n" + "\n".join(relations)

        sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)

        # 상위 K개 청크를 컨텍스트로 구성하고, 파일별 첫 200자를 출처 발췌로 사용
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
        """LLM 스트리밍 응답 생성.

        메시지 구성: system prompt → 참조 문서 컨텍스트 → 대화 이력(최근 20턴) → 현재 질의
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            messages.append({"role": "system", "content": f"[참조 문서]\n{context}"})

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
