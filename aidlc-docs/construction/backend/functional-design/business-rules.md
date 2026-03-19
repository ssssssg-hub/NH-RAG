# Backend Unit - Business Rules

## BR-B01: 세션 관리
- session_id가 없거나 유효하지 않으면 자동으로 신규 세션 생성
- 세션은 서버 메모리에 저장 (영구 저장 아님)
- 세션당 대화 이력은 최근 20턴으로 제한 (오래된 것부터 제거)

## BR-B02: 입력 검증
- message가 빈 문자열이면 400 에러 반환
- message 최대 길이: 2000자

## BR-B03: 하이브리드 검색
- Vector 검색과 Graph 검색을 병렬 수행
- 검색 결과가 없으면 context 없이 LLM에 질의 (일반 응답)
- RRF(k=60)로 결과 결합

## BR-B04: 프롬프트 구성
- system prompt: RAG 역할 정의 + 출처 기반 답변 지시
- context: 검색된 청크 + Graph 관계 정보
- history: 세션 내 이전 대화
- user query: 현재 질문

## BR-B05: 스트리밍 응답
- SSE 이벤트 타입: token, sources, done, error
- token: LLM 응답 토큰 단위 전송
- sources: 응답 완료 후 출처 정보 JSON 전송
- done: 스트림 종료 신호
- error: 에러 발생 시 에러 메시지 전송

## BR-B06: 출처 생성
- Vector 검색에서 반환된 청크의 file_name과 content를 출처로 사용
- 동일 문서의 여러 청크는 하나의 출처로 병합
- 원문 발췌는 200자로 제한

## BR-B07: 에러 처리
- LLM API 실패 시 SSE error 이벤트 전송
- 검색 실패 시 context 없이 LLM 호출 시도
- 전체 실패 시 "응답 생성에 실패했습니다. 다시 시도해주세요." 메시지
