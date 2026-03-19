# Integration Test Instructions

## Purpose
Unit 간 상호작용이 올바르게 동작하는지 검증합니다.

## 통합 테스트 시나리오

### Scenario 1: Batch → shared (문서 임베딩 파이프라인)

- **설명**: batch가 shared의 DB/Embeddings 모듈을 통해 문서를 처리하는 전체 흐름
- **사전 조건**: OpenAI 호환 API 접속 가능
- **테스트 절차**:
  1. `documents/` 디렉토리에 테스트 문서 배치 (예: `test_integration.txt`)
  2. 배치 실행: `python -m batch.batch`
  3. 검증:
     - `data/nh_rag.db`에 document_meta 레코드 생성 확인
     - `data/chromadb/`에 벡터 데이터 저장 확인
     - KùzuDB에 엔티티/관계 노드 생성 확인
  4. 동일 문서 재실행 → 변경 없음(skipped) 확인
  5. 문서 수정 후 재실행 → modified로 재처리 확인

```bash
# 테스트 문서 생성
echo "통합 테스트용 문서입니다. NH-RAG 시스템의 임베딩 파이프라인을 검증합니다." > documents/test_integration.txt

# 증분 실행
python -m batch.batch

# SQLite 확인
python -c "
import sqlite3
conn = sqlite3.connect('data/nh_rag.db')
rows = conn.execute('SELECT doc_id, status, chunk_count FROM document_meta').fetchall()
for r in rows: print(r)
conn.close()
"

# 변경 없이 재실행 → '변경된 문서 없음' 출력 확인
python -m batch.batch
```

### Scenario 2: Backend → shared (RAG 검색 파이프라인)

- **설명**: 백엔드가 shared의 ChromaDB/KùzuDB를 통해 검색하고 LLM 응답을 스트리밍
- **사전 조건**: Scenario 1 완료 (벡터 데이터 존재), OpenAI 호환 API 접속 가능
- **테스트 절차**:
  1. 백엔드 서버 시작: `python -m backend.app`
  2. 새 세션 생성 → 채팅 요청 → SSE 스트리밍 응답 확인

```bash
# 서버 시작 (별도 터미널)
python -m backend.app

# 세션 생성
curl -X POST http://localhost:8080/api/chat/new
# → {"session_id": "xxxxxxxx"}

# 채팅 요청 (SSE)
curl -N -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "통합 테스트 문서 내용을 알려줘", "session_id": "<위에서-받은-session_id>"}'
# → event: session, event: token (여러 번), event: sources, event: done
```

### Scenario 3: Frontend → Backend (E2E 사용자 흐름)

- **설명**: 브라우저에서 채팅 UI를 통해 질문 → 응답 스트리밍 → 출처 표시
- **사전 조건**: Scenario 1, 2 완료
- **테스트 절차**:
  1. 백엔드 서버 실행 중 확인
  2. 브라우저에서 `http://localhost:8080` 접속
  3. 채팅 입력란에 질문 입력 후 전송
  4. 검증:
     - 응답이 토큰 단위로 스트리밍되는지 확인
     - 출처 섹션이 접이식으로 표시되는지 확인
     - "새 대화" 버튼으로 세션 초기화 확인
     - 마크다운 렌더링 (코드 블록, 리스트 등) 확인

## Cleanup

```bash
# 테스트 데이터 정리
rm -f documents/test_integration.txt
rm -rf data/chromadb data/nh_rag.db
```
