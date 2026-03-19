# Batch Unit - NFR Design Patterns

## DP-01: Fail-Safe Processing (안정성)
- **패턴**: 문서 단위 try-except로 개별 실패 격리
- **적용**: 각 문서 처리를 독립적으로 감싸서 하나의 실패가 전체를 중단하지 않음
- **구현**: `for doc in documents: try: process(doc) except: log_error(doc)`

## DP-02: Idempotent Processing (데이터 무결성)
- **패턴**: 동일 입력에 대해 동일 결과 보장
- **적용**: ChromaDB upsert, KùzuDB MERGE 사용으로 중복 실행해도 안전
- **구현**: doc_id 기반 upsert/merge 연산

## DP-03: Change Detection (성능)
- **패턴**: SHA-256 해시 기반 변경 감지로 불필요한 재처리 방지
- **적용**: SQLite에 파일 해시 저장, 실행 시 비교하여 변경분만 처리
- **구현**: `hashlib.sha256(file_content).hexdigest()` 비교

## DP-04: Progress Reporting (운영성)
- **패턴**: Rich 라이브러리로 실시간 진행률 및 결과 테이블 출력
- **적용**: 문서 처리 중 진행률 바, 완료 후 결과 요약 테이블
- **구현**: `rich.progress.Progress`, `rich.table.Table`

## DP-05: Structured Logging (유지보수성)
- **패턴**: Python logging 모듈로 구조화된 로그
- **적용**: 레벨별 로그 (INFO: 처리 현황, WARNING: 건너뛴 파일, ERROR: 실패 상세)
- **구현**: `logging.getLogger(__name__)`

## DP-06: Configuration Externalization (유지보수성)
- **패턴**: 설정값을 코드에서 분리하여 중앙 관리
- **적용**: shared/config.py에서 모든 설정 관리 (DB 경로, API URL, 청크 크기 등)
- **구현**: Pydantic `BaseSettings` 또는 단순 상수 모듈
