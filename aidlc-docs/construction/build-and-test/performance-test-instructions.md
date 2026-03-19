# Performance Test Instructions

## Purpose
로컬 배포 환경에서 시스템이 요구사항(NFR)을 충족하는지 검증합니다.

## Performance Requirements (NFR 기준)
- **채팅 응답 첫 토큰**: < 3초 (LLM API 응답 시간 의존)
- **동시 사용자**: 5~10명 (내부 소규모 팀)
- **배치 처리**: 100개 문서 기준 30분 이내
- **메모리**: 백엔드 서버 2GB 이내

## 테스트 1: 채팅 응답 시간 측정

```bash
# 서버 시작 후 응답 시간 측정
time curl -s -N -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "테스트 질문입니다"}' \
  -o /dev/null -w "HTTP %{http_code}, TTFB: %{time_starttransfer}s, Total: %{time_total}s\n"
```

## 테스트 2: 동시 요청 처리

```bash
# 간단한 동시 요청 테스트 (5개 동시)
for i in $(seq 1 5); do
  curl -s -N -X POST http://localhost:8080/api/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"동시 요청 테스트 $i\"}" \
    -o /dev/null -w "Request $i: %{http_code} %{time_total}s\n" &
done
wait
```

## 테스트 3: 배치 처리 성능

```bash
# 테스트 문서 100개 생성
mkdir -p documents/perf_test
for i in $(seq 1 100); do
  python -c "print('성능 테스트 문서 $i. ' * 200)" > documents/perf_test/doc_$i.txt
done

# 전체 임베딩 시간 측정
time python -m batch.batch --full

# 정리
rm -rf documents/perf_test
```

## 테스트 4: 메모리 사용량

```bash
# 백엔드 서버 메모리 모니터링
python -m backend.app &
SERVER_PID=$!
sleep 3

# macOS
ps -o rss,vsz -p $SERVER_PID

# 정리
kill $SERVER_PID
```

## 판정 기준

| 항목 | 목표 | 판정 |
|---|---|---|
| 첫 토큰 응답 (TTFB) | < 3초 | TTFB 값 확인 |
| 동시 5요청 | 모두 200 OK | HTTP 코드 확인 |
| 배치 100문서 | < 30분 | time 출력 확인 |
| 서버 메모리 | < 2GB | RSS 값 확인 |
