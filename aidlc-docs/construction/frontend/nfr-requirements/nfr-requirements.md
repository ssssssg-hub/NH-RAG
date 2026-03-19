# Frontend Unit - NFR Requirements

## NFR-FE01: 반응성
- 모바일/데스크톱 모두 사용 가능한 반응형 레이아웃
- 채팅 영역이 화면 높이에 맞게 조절

## NFR-FE02: 사용성
- ChatGPT/Claude와 유사한 직관적 UI
- 스트리밍 중 로딩 인디케이터 표시
- 키보드 단축키 (Enter 전송, Shift+Enter 줄바꿈)

## NFR-FE03: 접근성
- 시맨틱 HTML 사용
- data-testid 속성으로 자동화 테스트 지원
- 적절한 색상 대비

## NFR-FE04: 성능
- VanillaJS로 프레임워크 오버헤드 없음
- 외부 CDN 의존 없음 (내부망)

## Tech Stack
- VanillaJS (프레임워크 없음)
- marked.js (마크다운 렌더링 - 로컬 번들)
- 순수 CSS (프레임워크 없음)
