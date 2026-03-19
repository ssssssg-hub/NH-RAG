# Services

## S1: ChatService

| 항목 | 내용 |
|---|---|
| **책임** | 채팅 요청 처리 오케스트레이션 |
| **호출 컴포넌트** | RAG Engine, SQLite Repository |

**오케스트레이션 흐름:**
1. 세션 ID 검증/생성
2. RAG Engine에 검색 요청 (질의 + 대화 이력)
3. 검색 결과 기반 LLM 스트리밍 응답 생성
4. 출처 정보와 함께 SSE 스트림 반환

---

## S2: EmbeddingService

| 항목 | 내용 |
|---|---|
| **책임** | 문서 임베딩 오케스트레이션 |
| **호출 컴포넌트** | Embedding Engine, ChromaDB Repository, Kuzu Repository, SQLite Repository |

**오케스트레이션 흐름:**
1. 변경 감지 (증분 모드) 또는 전체 스캔 (전체 모드)
2. 대상 문서 파싱 및 청킹
3. 청크 임베딩 → ChromaDB 저장
4. 엔티티 추출 → KùzuDB 저장
5. 문서 메타데이터(해시) 업데이트 → SQLite
6. 삭제된 문서 정리 (ChromaDB + KùzuDB + SQLite)
7. 실행 결과 반환

---

## 서비스 간 관계

```
[Frontend] --HTTP/SSE--> [API Server]
                              |
                         [ChatService]
                              |
                    +---------+---------+
                    |                   |
              [RAG Engine]      [SQLite Repo]
                    |
          +---------+---------+
          |                   |
   [ChromaDB Repo]    [Kuzu Repo]


[Batch CLI] --> [EmbeddingService]
                       |
              +--------+--------+---------+
              |        |        |         |
        [Embedding] [ChromaDB] [KùzuDB] [SQLite]
         [Engine]    [Repo]    [Repo]   [Repo]
```
