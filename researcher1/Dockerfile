# =====================================================================
# 연구자 1 이미지 : train.csv 전처리 → 모델링 → model.pkl 저장 자동화
# (현재 폴더 구조: researcher1/src/train.py, researcher1/src/data/*.csv)
# =====================================================================

# 디렉토리 경로: D:\minjae\sprint_mission\researcher1

# VSCode Docker Hub 이미지 build, run, tag, push 터미널 실행 명령어
# 디렉토리 이동
# cd researcher1

# 이미지 빌드
# docker build -t minjaejeon0827/mission15-trainer:v1.0.0 .

# (선택) 로컬에서 동작 확인 — 공유 볼륨에 model.pkl / test.csv 생성 확인
# docker run --rm -v shared-data:/app/output minjaejeon0827/mission15-trainer:v1.0.0

# (선택) Docker 컨테이너 안 파일 위치 직접 확인
# docker run --rm --entrypoint sh minjaejeon0827/mission15-trainer:v1.0.0 -c "find /app -name '*.py' -o -name '*.csv'"

# Docker Hub 로그인 후 push
# docker login
# docker push minjaejeon0827/mission15-trainer:v1.0.0

# 1. 베이스 이미지 (연구자 2와 동일한 파이썬 버전으로 고정 → 버전 통일)
FROM python:3.11-slim

# 2. 작업 디렉토리
WORKDIR /app

# 3. 의존성 먼저 설치 (레이어 캐싱 최적화)
#    requirements.txt 파일 바뀌지 않으면 pip install 레이어 캐시 재사용
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 데이터와 스크립트 복사 (자주 바뀌므로 뒤에 배치)
# src 폴더 통째로 복사 → /app/src/train.py, /app/src/data/*.csv 가 됨
COPY src/ ./src/

# 5. 환경 변수 (경로 및 파이썬 출력 버퍼링 해제)
# ★ 핵심: 데이터 경로 실제 위치(/app/src/data)로 지정
ENV DATA_DIR=/app/src/data \
    OUTPUT_DIR=/app/output \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 6. 모델/데이터가 저장될 출력 폴더 (공유 볼륨 마운트 지점)
RUN mkdir -p /app/output

# 7. 컨테이너 실행 시 자동으로 학습 스크립트 수행
#    Exec 형식 → PID 1 이 python 이 되어 시그널을 직접 수신
# ★ 핵심: 실제 파이썬 스크립트 파일 위치인 src/train.py 실행
ENTRYPOINT ["python", "src/train.py"]
