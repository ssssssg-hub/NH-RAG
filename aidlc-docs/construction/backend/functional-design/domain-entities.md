# Backend Unit - Domain Entities

## Entity: ChatRequest

| 필드 | 타입 | 설명 |
|---|---|---|
| message | str | 사용자 질문 텍스트 |
| session_id | str (optional) | 세션 ID (없으면 신규 생성) |

## Entity: ChatSession

| 필드 | 타입 | 설명 |
|---|---|---|
| session_id | str | UUID 기반 세션 식별자 |
| history | list[ChatMessage] | 대화 이력 (메모리 내) |
| created_at | datetime | 세션 생성 시각 |

## Entity: ChatMessage

| 필드 | 타입 | 설명 |
|---|---|---|
| role | str | "user" 또는 "assistant" |
| content | str | 메시지 내용 |

## Entity: SearchResult

| 필드 | 타입 | 설명 |
|---|---|---|
| context_chunks | list[ContextChunk] | 검색된 컨텍스트 청크 목록 |
| graph_context | list[dict] | Graph 검색 결과 (엔티티/관계) |

## Entity: ContextChunk

| 필드 | 타입 | 설명 |
|---|---|---|
| content | str | 청크 텍스트 |
| doc_id | str | 원본 문서 ID |
| file_name | str | 원본 파일명 |
| score | float | 유사도 점수 |

## Entity: Source

| 필드 | 타입 | 설명 |
|---|---|---|
| file_name | str | 참조 문서명 |
| excerpt | str | 관련 원문 발췌 |

## Entity: StreamEvent

| 필드 | 타입 | 설명 |
|---|---|---|
| event | str | "token", "sources", "done", "error" |
| data | str | 이벤트 데이터 (토큰 텍스트 / JSON) |
