@echo off
REM NH-RAG 문서 임베딩 배치 실행
REM Windows 작업 스케줄러에 등록하여 주기적 실행 가능

cd /d "%~dp0\.."
python -m batch.batch %*
pause
