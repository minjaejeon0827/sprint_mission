# 미션 소개

이번 미션은 두 명의 연구자가 협업하는 아래 시나리오를 참고하여 도커 기반 워크플로우를 설계하고, 
필요한 도커파일을 작성하는 미션입니다.

각 연구자에게 부여된 역할은 다음과 같습니다.

- **연구자 1**: 데이터 전처리, 탐색적 데이터 분석(EDA), 모델링 및 모델 파일 추출
- **연구자 2**: 추출된 모델을 활용한 추론

---

# 보고서

<a href="https://minjaejeon0827.github.io/sprint_mission15/reports/보고서.pdf">바로 가기</a>

---

# 프로젝트 구조

```
mission-result/
├── reports/
|   └── 보고서.pdf     # 보고서·발표자료 PDF
|
|   # 제출물 1: 코드 폴더
├── researcher1/  # 연구자 1
|   ├── src/
|   |   ├── data/     # mission15_train.csv, mission15_test.csv
|   |   ├── eda_modeling.ipynb  # 전처리·EDA·모델링 노트북
|   |   └── train.py
|   |
│   └── .dockerignore · Dockerfile · requirements.txt
│
├── researcher2/  # 연구자 2
|   ├── src/
|   |   └── work/inference.ipynb  # 추론 노트북
│   └── .dockerignore · Dockerfile · requirements.txt  # Jupyter 이미지
│
└── .dockerignore · docker-compose.yml · .env · README.md
```

---

# 사용 데이터셋

이번 미션의 데이터는 캐글에서 제공하는 [학생 성적 데이터](https://www.kaggle.com/datasets/nikhil7280/student-performance-multiple-linear-regression)를 스프린트 미션 전용으로 후처리한 데이터입니다.

아래 두 데이터를 다운로드 받아주세요.

- [train.csv](https://bakey-api.codeit.kr/api/files/resource?root=static&seqId=14111&version=1&directory=/mission15_train.csv&name=mission15_train.csv)
- [test.csv](https://bakey-api.codeit.kr/api/files/resource?root=static&seqId=14111&version=1&directory=/mission15_test.csv&name=mission15_test.csv)

| 변수명 | 설명 |
|---|---|
| Hours Studied | 각 학생이 공부에 소요한 총 시간 |
| Previous Scores | 학생들이 이전 시험에서 얻은 점수 |
| Extracurricular Activities | 학생이 과외 활동에 참여하는지 여부 (예 또는 아니오) |
| Sleep Hours | 학생이 하루 평균 수면 시간 |
| Sample Question Papers Practiced | 학생이 연습한 모의고사 수 |
| Performance Index | **목표변수.** 각 학생의 전반적인 성취도를 나타내는 지표 <br> (성취도 지수는 학생의 학업 성취도를 나타내며, 가장 가까운 정수로 반올림됩니다. <br>지수는 10에서 100까지이며, 값이 높을수록 더 나은 성취도를 나타냅니다.) |

---

# 협업 시나리오

```
1. [연구자 1]은 `train.csv` 데이터를 기반으로 Jupyter Notebook(`.ipynb`)에서 
   데이터 전처리, 탐색적 데이터 분석(EDA), 그리고 `scikit-learn`을 사용한 회귀 모델링을 수행한다. 
2. 모델 성능은 RMSE로 평가하며, 최종 모델은 `model.pkl` 파일로 저장한다. 
3. 이후, 전처리 - 모델링 - 모델 저장 과정을 하나의 `.py` 스크립트로 정리한다. 
4. [연구자 1]은 이 작업을 자동화하는 도커 이미지를 구축하여 Docker Hub에 업로드한다.
```

---

```
1. [연구자 2]는 [연구자 1]이 생성한 도커 이미지와 별도의 Jupyter Notebook 도커 이미지를 `docker-compose`로 구성한다.
2. [연구자 2]는 [연구자 1]의 도커 컨테이너에서 생성된 `model.pkl` 파일과 컨테이너 내부의 `test.csv` 파일을 활용하여 
   Jupyter Notebook 컨테이너에서 추론을 수행하고, 결과를 `result.csv` 파일로 저장한다. 
3. 전체 추론 과정이 담긴 inference.ipynb 파일을 별도로 저장한다.

(참고: [연구자 2]는 사전에 데이터나 모델 파일을 보유하지 않은 상태이며, 
      [연구자 1]의 Docker Hub 이미지를 통해 필요한 파일을 가져와야 한다.)
```

---

# 제출 안내

미션 15 폴더 하위에 {팀명}_{이름}으로 폴더를 생성하고, 그 안에 **코드 폴더**와 **보고서 pdf(2페이지 이내)**를 제출해 주세요.

1. **코드 폴더** (`mission-result`) : 실제 작성한 코드를 제출해주세요.
2. **보고서 PDF** (2페이지 이내) : 보고서 내용에는 다음의 항목들이 포함되어있어야 합니다.
   - Docker Hub URL
   - 연구자 1의 데이터 전처리 및 모델링 결과 요약
   - 코드 아키텍처 도식 및 설명

---

# 참고 사항

아래와 같은 내용을 신경써서 작업해주세요.

1. 두 연구자의 Python 버전과 패키지 버전을 동일하게 유지하는 방안
2. 연구자 1의 컨테이너에 있는 데이터와 `model.pkl` 파일을 연구자 2의 컨테이너로 전달하는 전략

- 힌트 : 두 컨테이너와 호스트 간 볼륨을 공유하고, `docker cp` 명령어를 활용한다.