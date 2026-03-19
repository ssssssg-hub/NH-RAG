# Batch Unit - Code Summary

## 생성된 파일

### shared/ (공통 모듈)
| 파일 | 역할 |
|---|---|
| `shared/__init__.py` | 패키지 초기화 |
| `shared/config.py` | 설정 중앙 관리 (환경변수 지원) |
| `shared/embeddings.py` | OpenAI 임베딩 API 호출 |
| `shared/db.py` | ChromaDB, KùzuDB, SQLite Repository |

### batch/ (배치 서비스)
| 파일 | 역할 |
|---|---|
| `batch/__init__.py` | 패키지 초기화 |
| `batch/embedding.py` | 문서 파싱, 청킹, 엔티티 추출, 변경 감지 |
| `batch/batch.py` | CLI 진입점, 오케스트레이션, Rich 출력 |
| `batch/run_embedding.bat` | Windows 스케줄러용 .bat |

### tests/
| 파일 | 테스트 대상 |
|---|---|
| `tests/test_shared_embeddings.py` | 임베딩 API 호출 |
| `tests/test_shared_db.py` | SQLite CRUD |
| `tests/test_batch_embedding.py` | 파싱, 청킹, 변경 감지 |
| `tests/test_batch_main.py` | CLI 오케스트레이션 |

## 실행 방법

```bash
# 증분 임베딩
python -m batch.batch

# 전체 재임베딩
python -m batch.batch --full

# Windows .bat
batch\run_embedding.bat
batch\run_embedding.bat --full
```

## Story 구현 현황
- [x] US-07: 수동 문서 임베딩 실행
- [x] US-08: 증분 임베딩
- [x] US-09: 스케줄 기반 자동 임베딩 (.bat)
- [x] US-10: 전체 재임베딩
- [x] US-11: 문서 배치 및 형식 안내
