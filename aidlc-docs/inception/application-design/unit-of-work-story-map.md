# Unit of Work - Story Map

## Unit 1: Frontend

| Story | 우선순위 | 설명 |
|---|---|---|
| US-01 | Must | 질문 입력 및 전송 |
| US-02 | Must | 스트리밍 응답 표시 |
| US-04 | Must | 출처 표시 |
| US-05 | Must | 세션 내 대화 이력 유지 |
| US-06 | Should | 새 대화 시작 |

## Unit 2: Backend

| Story | 우선순위 | 설명 |
|---|---|---|
| US-01 | Must | 질문 입력 및 전송 (API 엔드포인트) |
| US-02 | Must | 스트리밍 응답 (SSE) |
| US-03 | Must | 하이브리드 검색 기반 답변 |
| US-04 | Must | 출처 표시 (출처 데이터 생성) |
| US-05 | Must | 세션 내 대화 이력 (멀티턴 context) |
| US-06 | Should | 새 대화 시작 (세션 초기화 API) |

## Unit 3: Batch

| Story | 우선순위 | 설명 |
|---|---|---|
| US-07 | Must | 수동 문서 임베딩 실행 |
| US-08 | Must | 증분 임베딩 |
| US-09 | Should | 스케줄 기반 자동 임베딩 (.bat) |
| US-10 | Should | 전체 재임베딩 |
| US-11 | Must | 문서 배치 및 형식 안내 |

## 커버리지 검증

| Story | Unit 1 | Unit 2 | Unit 3 |
|---|---|---|---|
| US-01 | ✅ | ✅ | |
| US-02 | ✅ | ✅ | |
| US-03 | | ✅ | |
| US-04 | ✅ | ✅ | |
| US-05 | ✅ | ✅ | |
| US-06 | ✅ | ✅ | |
| US-07 | | | ✅ |
| US-08 | | | ✅ |
| US-09 | | | ✅ |
| US-10 | | | ✅ |
| US-11 | | | ✅ |

모든 11개 스토리가 Unit에 할당됨 ✅
