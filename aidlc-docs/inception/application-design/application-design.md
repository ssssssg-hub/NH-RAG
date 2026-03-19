# NH-RAG Application Design (통합)

## 1. 아키텍처 개요

NH-RAG는 레이어드 아키텍처로 구성되며, 크게 두 가지 실행 경로를 가집니다:
- **실시간 경로**: Frontend → API Server → ChatService → RAG Engine → DB
- **배치 경로**: CLI/Bat → Batch Service → EmbeddingService → Embedding Engine → DB

## 2. 컴포넌트 (6개)

| ID | 컴포넌트 | 기술 | 핵심 책임 |
|---|---|---|---|
| C1 | Frontend | VanillaJS | 채팅 UI, SSE 스트리밍 수신 |
| C2 | API Server | FastAPI | HTTP/SSE 엔드포인트 |
| C3 | RAG Engine | Python | Vector+Graph 하이브리드 검색, LLM 호출 |
| C4 | Embedding Engine | Python | 문서 파싱, 청킹, 임베딩, 엔티티 추출 |
| C5 | Batch Service | Python+Bat | 임베딩 실행 오케스트레이션 |
| C6 | Data Access Layer | Python | ChromaDB/KùzuDB/SQLite CRUD 추상화 |

## 3. 서비스 (2개)

| ID | 서비스 | 오케스트레이션 |
|---|---|---|
| S1 | ChatService | 세션 관리 → RAG 검색 → LLM 스트리밍 → 출처 반환 |
| S2 | EmbeddingService | 변경 감지 → 파싱/청킹 → 임베딩 → 그래프 저장 → 메타 업데이트 |

## 3. 시스템 구조도

```
+------------------+          +------------------+
|   C1: Frontend   |--HTTP--->|  C2: API Server  |
|   (VanillaJS)    |<--SSE----|  (FastAPI)       |
+------------------+          +--------+---------+
                                       |
                              +--------+---------+
                              |  S1: ChatService |
                              +--------+---------+
                                       |
                              +--------+---------+
                              |  C3: RAG Engine  |
                              +--+-----+-----+--+
                                 |     |     |
                    +------------+  +--+--+  +----------+
                    |               |     |             |
              +-----+------+ +-----+--+ +------+  +----+----+
              |C6: ChromaDB| |C6:KùzuDB| |C6:SQL|  |OpenAI   |
              |  Repo      | |  Repo  | | Repo |  |API(내부)|
              +-----+------+ +---+----+ +--+---+  +---------+
                    |            |         |
              +-----+------+ +--+-----+ +-+-------+
              |  ChromaDB   | | KùzuDB | | SQLite  |
              +-------------+ +--------+ +---------+

+------------------+
| C5: Batch Service|
| (CLI / .bat)     |
+--------+---------+
         |
+--------+---------+
|S2:EmbeddingService|
+--------+---------+
         |
+--------+---------+
|C4:Embedding Engine|
+--+-----+-----+--+
   |     |     |
   v     v     v
ChromaDB KùzuDB SQLite + OpenAI API(내부)
```

## 4. 주요 설계 결정

| 결정 | 선택 | 근거 |
|---|---|---|
| 백엔드 프레임워크 | FastAPI | 비동기 지원, SSE 스트리밍, 경량, Python 생태계 |
| 스트리밍 방식 | SSE (Server-Sent Events) | WebSocket보다 단순, 단방향 스트리밍에 적합 |
| 검색 결합 | Reciprocal Rank Fusion | Vector/Graph 결과를 스코어 기반으로 공정하게 결합 |
| 변경 감지 | 파일 해시 (SHA-256) | 파일 내용 기반 정확한 변경 감지 |
| 엔티티 추출 | LLM 기반 | 별도 NER 모델 설치 불필요, 내부 API 활용 |

## 5. 요구사항 매핑

| 요구사항 | 컴포넌트 |
|---|---|
| FR-01 채팅 인터페이스 | C1, C2 |
| FR-02 대화 이력 | C1 (클라이언트), S1 |
| FR-03 RAG 검색 | C3, C6 |
| FR-04 Batch 임베딩 | C4, C5, C6 |
| FR-05 문서 관리 | C4, C5 |
| NFR-01 성능 | C2 (FastAPI 비동기), C3 (병렬 검색) |
| NFR-02 저장소 | C6 (SQLite) |
| NFR-03 배포 | C5 (.bat), 전체 (python 직접 실행) |
| NFR-04 확장성 | C4 (파서 확장), C6 (저장소 교체) |
