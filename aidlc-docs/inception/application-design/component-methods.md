# Component Methods

> 비즈니스 규칙 상세는 Functional Design(CONSTRUCTION)에서 정의됩니다.

---

## C1: Frontend

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `sendMessage(text)` | string | void | 사용자 메시지 전송 및 SSE 스트리밍 시작 |
| `renderStreamChunk(chunk)` | string | void | 스트리밍 청크를 채팅 영역에 렌더링 |
| `renderSources(sources)` | Source[] | void | 출처 정보 렌더링 |
| `startNewChat()` | void | void | 대화 초기화 및 새 세션 시작 |
| `appendMessage(role, content)` | string, string | void | 채팅 영역에 메시지 추가 |

---

## C2: API Server

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `POST /api/chat` | `{message, session_id}` | SSE stream | 채팅 질의 처리 및 스트리밍 응답 |
| `POST /api/chat/new` | void | `{session_id}` | 새 채팅 세션 생성 |

---

## C3: RAG Engine

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `search(query, chat_history)` | str, list | SearchResult | 하이브리드 검색 수행 |
| `vector_search(query_embedding)` | list[float] | list[VectorResult] | ChromaDB 유사도 검색 |
| `graph_search(query)` | str | list[GraphResult] | KùzuDB 엔티티/관계 검색 |
| `merge_results(vector, graph)` | list, list | list[MergedResult] | RRF 기반 결과 결합 |
| `generate_stream(query, context, history)` | str, list, list | AsyncGenerator | LLM 스트리밍 응답 생성 |
| `embed_query(text)` | str | list[float] | 질의 텍스트 임베딩 |

---

## C4: Embedding Engine

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `process_documents(doc_dir, full)` | str, bool | EmbeddingResult | 문서 임베딩 메인 로직 |
| `parse_document(file_path)` | str | list[Chunk] | 문서 파싱 및 청킹 |
| `embed_chunks(chunks)` | list[Chunk] | list[EmbeddedChunk] | 청크 임베딩 |
| `extract_entities(chunks)` | list[Chunk] | list[Entity] | 엔티티/관계 추출 (LLM 활용) |
| `detect_changes(doc_dir)` | str | ChangeSet | 파일 해시 비교로 변경 감지 |

---

## C5: Batch Service

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `run(full=False)` | bool | BatchResult | 임베딩 실행 오케스트레이션 |
| `print_summary(result)` | BatchResult | void | 실행 결과 콘솔 출력 |

---

## C6: Data Access Layer

### ChromaDB Repository
| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `upsert(doc_id, chunks, embeddings)` | str, list, list | void | 벡터 저장/갱신 |
| `search(embedding, top_k)` | list[float], int | list[VectorResult] | 유사도 검색 |
| `delete(doc_id)` | str | void | 문서 벡터 삭제 |

### KuzuRepository
| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `upsert_entities(doc_id, entities)` | str, list[Entity] | void | 엔티티/관계 저장 |
| `search_related(entity_names)` | list[str] | list[GraphResult] | 관련 엔티티/관계 검색 |
| `delete_by_doc(doc_id)` | str | void | 문서 관련 그래프 데이터 삭제 |

### SQLite Repository
| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `save_doc_meta(doc_id, hash, status)` | str, str, str | void | 문서 메타데이터 저장 |
| `get_doc_meta(doc_id)` | str | DocMeta | 문서 메타데이터 조회 |
| `save_batch_log(result)` | BatchResult | void | Batch 실행 이력 저장 |
| `get_all_doc_hashes()` | void | dict[str,str] | 전체 문서 해시 조회 |
