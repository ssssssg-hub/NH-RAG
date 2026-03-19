# Batch Unit - Tech Stack Decisions

## 핵심 기술

| 기술 | 선택 | 근거 |
|---|---|---|
| Python | 3.11.9 | 프로젝트 제약사항 |
| OpenAI Client | `openai` | 내부 OpenAI 호환 API 호출 |
| ChromaDB | `chromadb` | 벡터 저장/검색 |
| KùzuDB | `kuzu` | 임베디드 그래프 DB |
| SQLite | `sqlite3` (표준) | 메타데이터/이력 저장 |
| LangChain | `langchain`, `langchain-openai` | 문서 로더, 텍스트 스플리터, 임베딩 추상화 |
| Pydantic | `pydantic` | 데이터 모델 검증, 엔티티 스키마 정의 |
| Rich | `rich` | 콘솔 출력 포맷팅 (진행률, 테이블, 색상) |

## 패키지 의존성 (requirements.txt)

```
openai
chromadb
kuzu
langchain
langchain-openai
langchain-community
pydantic
rich
```

## LangChain 활용 범위

| 기능 | LangChain 활용 | 직접 구현 |
|---|---|---|
| 문서 로딩 | `TextLoader`, `CSVLoader`, `UnstructuredMarkdownLoader` | |
| 텍스트 분할 | `RecursiveCharacterTextSplitter` | |
| 임베딩 | `OpenAIEmbeddings` (base_url 커스텀) | |
| 엔티티 추출 | | LLM 프롬프트 + Pydantic 스키마 |
| 변경 감지 | | SHA-256 해시 비교 |
| DB 저장 | | ChromaDB/KùzuDB 직접 접근 |

> LangChain은 문서 로딩/분할/임베딩 등 잘 추상화된 부분만 활용하고, 비즈니스 로직(변경 감지, 엔티티 추출, DB 저장)은 직접 구현하여 제어권 유지.

## 설계 원칙
- 개발 생산성에 도움되는 프레임워크/라이브러리 적극 활용
- 내부망 반입은 패키지 목록만 있으면 가능하므로 제약 없음
- 단, 과도한 의존성 체인은 지양 (핵심 라이브러리 위주)
