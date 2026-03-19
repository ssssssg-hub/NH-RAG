# Frontend Unit - Code Summary

## 생성된 파일

| 파일 | 역할 |
|---|---|
| `frontend/index.html` | 메인 페이지 (시맨틱 HTML, data-testid) |
| `frontend/css/style.css` | 다크 테마 스타일, 반응형 레이아웃 |
| `frontend/js/app.js` | 채팅 로직, SSE 스트리밍, 출처 표시, 마크다운 렌더링 |

## 주요 기능
- SSE 스트리밍 수신 및 실시간 토큰 렌더링
- 접이식 출처 표시 (문서명 + 원문 발췌)
- 세션 관리 (메모리 내 session_id)
- 새 대화 시작
- Enter 전송 / Shift+Enter 줄바꿈
- 자동 스크롤, 타이핑 인디케이터
- 경량 마크다운 렌더링 (코드 블록, 볼드, 리스트)
- 다크 테마, 반응형 (모바일/데스크톱)

## Story 구현 현황
- [x] US-01: 질문 입력 및 전송
- [x] US-02: 스트리밍 응답 표시
- [x] US-04: 출처 표시
- [x] US-05: 세션 내 대화 이력 유지
- [x] US-06: 새 대화 시작
