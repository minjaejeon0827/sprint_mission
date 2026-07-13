# =====================================================================
# 연구자 2 이미지 : 추론용 Jupyter Notebook(Lab) 환경
# 연구자 1 과 "동일한 python:3.11-slim + 동일 패키지 버전" 으로 빌드하여
# model.pkl 의 pickle 호환성(특히 scikit-learn 버전)을 보장한다.
# =====================================================================

# 1. 연구자 1과 동일한 베이스 이미지 → 파이썬 버전 통일
FROM python:3.11-slim

# 2. 의존성 설치 (레이어 캐싱 최적화)
WORKDIR /tmp
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. 연구자 2 작업 디렉토리 및 공유 볼륨 마운트 지점
#    /home/jovyan/work   : inference.ipynb 및 result.csv (호스트 바인드)
#    /home/jovyan/shared : 연구자 1이 넘겨준 model.pkl / test.csv (공유 볼륨)
RUN mkdir -p /home/jovyan/work /home/jovyan/shared
WORKDIR /home/jovyan/work

# 4. 파이썬 출력 버퍼링 해제
ENV PYTHONUNBUFFERED=1

# 5. JupyterLab 실행
EXPOSE 8888
ENTRYPOINT ["jupyter", "lab", \
    "--ip=0.0.0.0", "--port=8888", "--no-browser", \
    "--allow-root", "--ServerApp.root_dir=/home/jovyan"]