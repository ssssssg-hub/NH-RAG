# Backend Unit - NFR Requirements

## NFR-BE01: 성능
- SSE 스트리밍 첫 토큰: LLM API 응답 속도에 의존
- Vector + Graph 검색: 2초 이내 (소규모 데이터)
- 동시 사용자 5명 이하 처리

## NFR-BE02: 안정성
- LLM API 실패 시 graceful degradation (에러 메시지 반환)
- 검색 실패 시 context 없이 LLM 호출 (fallback)
- 비동기 처리로 요청 간 블로킹 방지

## NFR-BE03: 확장성
- 세션 관리: 메모리 → Redis 등으로 교체 가능한 구조
- 대화 이력: 세션 기반 → 영구 저장으로 확장 가능
- 정적 파일 서빙: 추후 Nginx 등으로 분리 가능

## NFR-BE04: 유지보수성
- 라우터/서비스/엔진 레이어 분리
- 설정은 shared/config.py 중앙 관리
- Python logging 모듈 사용
