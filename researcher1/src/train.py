"""
=====================================================================
연구자 1 : 전처리 - 모델링 - 모델 저장 자동화 스크립트
---------------------------------------------------------------------
협업 시나리오 3~4단계 해당.
Jupyter Notebook(eda_modeling.ipynb)에서 확정한 파이프라인을 하나의 .py 스크립트로 정리한 것으로, 
이 스크립트를 실행하는 것이 곧 도커 이미지 기본 동작(ENTRYPOINT) 의미.

VSCode 터미널 실행 명령어
  - $env:DATA_DIR="./data"
  - $env:OUTPUT_DIR="./output"
  - python train.py

동작 순서
  1) data/mission15_train.csv 로드
  2) 범주형(Extracurricular Activities) 인코딩 + 수치형 통과 파이프라인 구성
  3) 학습/검증 분할 및 RMSE 평가 (성능 로그 출력)
  4) 전체 데이터로 재학습 후 model.pkl 저장
  5) 연구자 2 에게 넘겨줄 test.csv 파일 출력 폴더로 복사
=====================================================================
"""

# ── 모듈 임포트(필요한 도구 불러오기) ────────────────────────────
import os        # 환경변수 읽기, 경로 조합, 폴더 생성 등 OS 기능
import shutil    # 파일 복사 같은 고수준 파일 작업 (test.csv 복사에 사용)

import numpy as np   # 수치 계산 라이브러리 (여기선 제곱근 np.sqrt 계산)
import pandas as pd  # 표(DataFrame) 형태 데이터 처리, CSV 읽기
import joblib        # 학습된 모델 객체를 .pkl 파일로 저장/불러오기

from sklearn.compose import ColumnTransformer        # 컬럼마다 다른 전처리를 적용하는 도구
from sklearn.pipeline import Pipeline                # 전처리 + 모델을 하나로 묶는 도구
from sklearn.preprocessing import OrdinalEncoder     # 범주형(Yes/No)을 숫자(0/1)로 변환
from sklearn.linear_model import LinearRegression    # 선형회귀 모델(예측 알고리즘)
from sklearn.model_selection import train_test_split # 데이터를 학습용/검증용으로 나눔
from sklearn.metrics import mean_squared_error, r2_score  # 성능 평가 지표(RMSE 계산용, R²)

# ── 경로·상수 설정 ───────────────────────────────────────────────
# os.environ.get("키", "기본값"): 환경변수 '키'가 있으면 그 값을, 없으면 기본값 사용
DATA_DIR = os.environ.get("DATA_DIR", "/app/data")       # 입력 데이터 폴더(컨테이너 기준 /app/data)
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app/output") # 결과 저장 폴더(공유 볼륨이 연결되는 곳)
TARGET = "Performance Index"                  # 예측 대상(목표변수)이 되는 컬럼 이름
CATEGORICAL = ["Extracurricular Activities"]  # 범주형(글자로 된) 컬럼 이름 목록

os.makedirs(OUTPUT_DIR, exist_ok=True)  # 출력 폴더 생성. exist_ok=True → 이미 있으면 에러 없이 넘어감


# ── 전처리+모델 파이프라인 만들어 주는 함수 ─────────────────────
def build_pipeline(feature_columns):
    """수치형 그대로 통과, 범주형(Yes/No) OrdinalEncoder로 0/1 인코딩."""
    # 전달받은 전체 컬럼 중 범주형이 아닌 것들 = 수치형 컬럼 목록
    numeric = [c for c in feature_columns if c not in CATEGORICAL]

    # ColumnTransformer: "어떤 컬럼에 어떤 변환 적용할지" 정의
    pre = ColumnTransformer(
        transformers=[
            # ("이름", 변환기, 대상컬럼) → 범주형 컬럼에만 OrdinalEncoder 적용
            # categories=[["No", "Yes"]] → No를 0, Yes를 1로 '순서를 고정'해서 인코딩
            ("cat", OrdinalEncoder(categories=[["No", "Yes"]]), CATEGORICAL),
        ],
        remainder="passthrough",  # 위에서 안 다룬 나머지 컬럼(수치형 5개)은 변환 없이 그대로 통과
    )

    # Pipeline: 여러 단계를 순서대로 묶음. 먼저 전처리(pre) → 그다음 선형회귀(reg)
    # 이렇게 묶으면 학습·예측 때 전처리가 자동으로 같이 적용됨
    return Pipeline([("pre", pre), ("reg", LinearRegression())]), numeric


# ── 실제 작업을 수행하는 메인 함수 ───────────────────────────────
def main():
    # os.path.join: 폴더 경로와 파일명을 OS에 맞게 안전하게 합침
    train_path = os.path.join(DATA_DIR, "mission15_train.csv")  # 학습 데이터 파일 경로
    test_path = os.path.join(DATA_DIR, "mission15_test.csv")    # 테스트 데이터 파일 경로

    print(f"[1/5] 학습 데이터 로드: {train_path}")
    df = pd.read_csv(train_path)  # CSV 파일을 읽어 표(DataFrame)로 만듦
    # df.shape → (행 수, 열 수),  isnull().sum().sum() → 전체 결측치 개수 합계
    print(f"      shape={df.shape}, 결측치 총합={int(df.isnull().sum().sum())}")

    X = df.drop(columns=[TARGET])  # 입력(X): 목표변수 컬럼을 뺀 나머지 전부 = 5개 특성
    y = df[TARGET]                 # 정답(y): 목표변수 컬럼(Performance Index)만

    print("[2/5] 전처리 파이프라인 구성 (범주형 인코딩 + 선형회귀)")
    pipe, numeric = build_pipeline(X.columns)  # 위 함수로 파이프라인 생성
    print(f"      수치형={numeric}")
    print(f"      범주형={CATEGORICAL}")

    print("[3/5] 학습/검증 분할(8:2) 및 RMSE 평가")
    # train_test_split: 데이터 학습용 80% / 검증용 20% 분할
    # random_state=42: 나누는 방식 고정 → 매번 같은 결과(재현성 확보)
    X_tr, X_val, y_tr, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    pipe.fit(X_tr, y_tr)          # 학습용 데이터로 모델 학습(전처리+회귀가 함께 학습됨)
    val_pred = pipe.predict(X_val)  # 검증용 입력으로 예측값 생성

    # mean_squared_error(정답, 예측) = MSE(평균제곱오차), np.sqrt로 제곱근 → RMSE
    # RMSE: 예측이 실제값과 평균적으로 얼마나 벗어나는지(작을수록 좋음)
    rmse = float(np.sqrt(mean_squared_error(y_val, val_pred)))
    # r2_score: 결정계수(1에 가까울수록 잘 맞춤)
    r2 = float(r2_score(y_val, val_pred))
    print(f"      >>> 검증 RMSE = {rmse:.5f}")  # 소수점 5자리까지 출력
    print(f"      >>> 검증 R^2  = {r2:.5f}")

    print("[4/5] 전체 데이터 재학습 후 model.pkl 저장")
    pipe.fit(X, y)  # 검증 끝났으니, 이번엔 데이터 100% 다시 학습(최종 모델 만들기)
    model_path = os.path.join(OUTPUT_DIR, "model.pkl")  # 저장할 파일 경로
    joblib.dump(pipe, model_path)  # 파이프라인(전처리+모델)을 통째로 .pkl 파일 저장
    print(f"      저장 완료: {model_path}")

    print("[5/5] 연구자 2 에게 전달할 test.csv 출력 폴더 복사")
    # test.csv 출력 폴더(공유 볼륨)로 복사 → 연구자 2가 추론에 사용
    shutil.copy(test_path, os.path.join(OUTPUT_DIR, "mission15_test.csv"))
    print(f"      복사 완료: {os.path.join(OUTPUT_DIR, 'mission15_test.csv')}")

    print("\n[완료] model.pkl 과 test.csv 파일 공유 볼륨 준비 완료.")


# ── 스크립트 실행 진입점 ─────────────────────────────────────────
# 이 파일을 'python train.py' 명령어 직접 실행할 때만 main() 함수 실행
# (다른 파일에서 import될 때는 자동 실행되지 않도록 하는 파이썬 관용구)
if __name__ == "__main__":
    main()