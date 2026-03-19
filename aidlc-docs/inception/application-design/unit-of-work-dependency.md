# Unit of Work Dependencies

## 의존성 매트릭스

| Unit | 의존 대상 | 통신 방식 | 설명 |
|---|---|---|---|
| Unit 1 (Frontend) | Unit 2 (Backend) | HTTP REST + SSE | 채팅 API 호출, 스트리밍 응답 수신 |
| Unit 2 (Backend) | shared | Python import | config, db, embeddings |
| Unit 2 (Backend) | 내부 OpenAI API | HTTP (via shared) | LLM 응답 생성 |
| Unit 3 (Batch) | shared | Python import | config, db, embeddings |
| Unit 3 (Batch) | 내부 OpenAI API | HTTP (via shared) | 임베딩 + 엔티티 추출 |

## Unit 간 관계

```
+-------------------+
| Unit 1: Frontend  |
+--------+----------+
         | HTTP/SSE
         v
+--------+----------+     +-------------------+
| Unit 2: Backend   |     | Unit 3: Batch     |
+--------+----------+     +--------+----------+
         |                         |
         +----------+--------------+
                    |
              +-----+------+
              |   shared   |
              | config/db/ |
              | embeddings |
              +-----+------+
                    |
         +----+----+----+----+
         |    |    |         |
         v    v    v         v
      ChromaDB KùzuDB SQLite OpenAI API
```

## 개발 순서 (권장)

1. **shared** → 공통 모듈 먼저 (config, db, embeddings)
2. **Unit 3 (Batch)** → 문서 임베딩 (검색 테스트용 데이터 생성)
3. **Unit 2 (Backend)** → RAG 검색 + API
4. **Unit 1 (Frontend)** → 채팅 UI 연동
