# Build Instructions

## Prerequisites
- **Python**: 3.11.9
- **pip**: 최신 버전 권장
- **KùzuDB**: 임베디드 그래프 DB (별도 서버 불필요, data/kuzudb에 자동 생성)
- **OS**: Windows (운영), macOS/Linux (개발)

## 환경 변수

| 변수 | 설명 | 기본값 |
|---|---|---|
| `NH_RAG_DOCUMENTS_DIR` | 임베딩 대상 문서 경로 | `./documents` |
| `NH_RAG_DATA_DIR` | SQLite/ChromaDB 데이터 경로 | `./data` |
| `NH_RAG_OPENAI_API_BASE` | 내부 OpenAI 호환 API URL | `http://localhost:8000/v1` |
| `NH_RAG_OPENAI_API_KEY` | API 키 | `internal-key` |
| `NH_RAG_EMBEDDING_MODEL` | 임베딩 모델명 | `text-embedding-ada-002` |
| `NH_RAG_CHAT_MODEL` | 채팅 모델명 | `gpt-4` |

## Build Steps

### 1. 가상환경 생성 및 활성화
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 디렉토리 준비
```bash
mkdir -p documents data
```

### 4. 환경 변수 설정 (필요 시)
```bash
# .env 파일 또는 직접 export
export NH_RAG_OPENAI_API_BASE="http://<내부-API-서버>:8000/v1"
export NH_RAG_OPENAI_API_KEY="<발급받은-키>"
```

### 5. 빌드 검증
```bash
# 모듈 import 확인
python -c "from shared.config import PROJECT_ROOT; print(f'OK: {PROJECT_ROOT}')"
python -c "from backend.app import app; print('FastAPI OK')"
python -c "from batch.batch import main; print('Batch OK')"
```

## 실행 방법

### 배치 임베딩 (문서 → 벡터DB)
```bash
# 증분 임베딩
python -m batch.batch

# 전체 재임베딩
python -m batch.batch --full
```

### 백엔드 서버 시작
```bash
python -m backend.app
# → http://localhost:8080 에서 서비스 접속
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'shared'`
- 프로젝트 루트에서 실행하고 있는지 확인
- `sys.path`에 프로젝트 루트가 포함되어 있는지 확인

### ChromaDB 초기화 오류
- `data/chromadb` 디렉토리 삭제 후 재시도: `rm -rf data/chromadb`

### KùzuDB 초기화 오류
- `data/kuzudb` 디렉토리 삭제 후 재시도: `rm -rf data/kuzudb`
- 배치/백엔드는 KùzuDB 연결 실패 시 Graceful Degradation (Vector 검색만 동작)
