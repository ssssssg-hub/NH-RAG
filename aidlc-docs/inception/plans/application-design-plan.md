# Application Design Plan

## 설계 계획

### Step 1: 컴포넌트 식별 및 정의
- [x] 프론트엔드 컴포넌트 정의
- [x] 백엔드 API 서버 컴포넌트 정의
- [x] RAG 검색 엔진 컴포넌트 정의
- [x] Batch 임베딩 컴포넌트 정의
- [x] 데이터 액세스 컴포넌트 정의
- [x] components.md 생성

### Step 2: 컴포넌트 메서드 정의
- [x] 각 컴포넌트별 메서드 시그니처 정의
- [x] 입출력 타입 정의
- [x] component-methods.md 생성

### Step 3: 서비스 레이어 설계
- [x] 서비스 정의 및 오케스트레이션 패턴
- [x] services.md 생성

### Step 4: 컴포넌트 의존성 설계
- [x] 의존성 매트릭스
- [x] 통신 패턴 및 데이터 흐름
- [x] component-dependency.md 생성

### Step 5: 통합 문서
- [x] application-design.md 통합 문서 생성

### Step 6: 검증
- [x] 모든 FR/NFR 커버리지 확인
- [x] 컴포넌트 간 일관성 검증

---

## 질문

이 프로젝트의 요구사항과 기술 스택이 충분히 명확하므로 (Python 3.11.9, VanillaJS, ChromaDB, KùzuDB, SQLite, 내부 OpenAI API) 추가 질문 없이 설계를 진행합니다.

**설계 결정 사항:**
- 백엔드 프레임워크: FastAPI (비동기 스트리밍 지원, 경량)
- 프론트엔드-백엔드 통신: SSE (Server-Sent Events) for 스트리밍
- 컴포넌트 구조: 레이어드 아키텍처 (Controller → Service → Repository)
