# Batch Unit - Logical Components

## 컴포넌트 구성

```
batch/
  batch.py          # CLI 진입점 + 오케스트레이션
  embedding.py      # 문서 파싱, 청킹, 임베딩, 엔티티 추출

shared/
  config.py         # 설정 중앙 관리
  db.py             # DB 접근 (ChromaDB, KùzuDB, SQLite)
  embeddings.py     # OpenAI 임베딩 API 호출
```

## 컴포넌트별 NFR 패턴 매핑

| 컴포넌트 | 적용 패턴 |
|---|---|
| batch.py | DP-01 (Fail-Safe), DP-04 (Progress Reporting) |
| embedding.py | DP-02 (Idempotent), DP-03 (Change Detection) |
| shared/config.py | DP-06 (Configuration Externalization) |
| shared/db.py | DP-02 (Idempotent - upsert/merge) |
| 전체 | DP-05 (Structured Logging) |

## 외부 의존 컴포넌트

| 컴포넌트 | 유형 | 비고 |
|---|---|---|
| ChromaDB | Python 내장 실행 | 별도 서버 불필요, data/ 디렉토리에 저장 |
| KùzuDB | 임베디드 (서버 불필요) | data/kuzudb에 저장 |
| SQLite | Python 표준 라이브러리 | data/nh_rag.db |
| 내부 OpenAI API | HTTP 서비스 | 내부망 제공 |
