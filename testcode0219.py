

import pandas as pd
from autogluon.tabular import TabularPredictor
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import torch
print(torch.cuda.is_available())  # GPU 사용 가능 여부 (True/False)
print(torch.cuda.device_count())  # 사용 가능한 GPU 개수
print(torch.cuda.get_device_name(0))  # 첫 번째 GPU의 이름 출력 (GPU가 있을 경우)

#########################################

#########################################
def preprocess_data(df):

    # 제거할 컬럼
    drop_columns = [
        '불임 원인 - 자궁경부 문제', '미세주입 후 저장된 배아 수', '불임 원인 - 정자 면역학적 요인',
        '불임 원인 - 정자 운동성', '시술 유형', '난자 해동 경과일', 'DI 출산 횟수', '저장된 신선 난자 수',
        '정자 출처', '임신 시도 또는 마지막 임신 경과 연수',
        '부부 부 불임 원인', '여성 부 불임 원인', '불임 원인 - 정자 형태', '대리모 여부', '불임 원인 - 정자 농도',
        '착상 전 유전 진단 사용 여부', '기증 배아 사용 여부'
    ]

    df = df.drop(columns=[col for col in drop_columns if col in df.columns])

    # ✅ 피처 엔지니어링 적용
    df["배아 수 제곱"] = df["이식된 배아 수"] ** 2



    # ✅ 연령대를 중앙값으로 변환하여 숫자로 변환
    age_mapping = {
        "만18-34세": 26,
        "만35-37세": 36,
        "만38-39세": 38.5,
        "만40-42세": 41,
        "만43-44세": 43.5,
        "만45-50세": 47.5,
        "알 수 없음": -1  # "알 수 없음"을 특별한 값으로 처리
    }

    # ✅ 매핑 적용
    df["시술 당시 나이 숫자"] = df["시술 당시 나이"].map(age_mapping)

    # 배아 개수 대비 저장된 배아 수 비율 (배아 보존율)
    df["배아 보존율"] = df["저장된 배아 수"] / (df["총 생성 배아 수"] + 1)  # 0으로 나누는 것 방지
    df["이식 배아 비율"] = df["이식된 배아 수"] / (df["총 생성 배아 수"] + 1)
    df["배아 보존율 제곱"] =  df["배아 보존율"]* df["배아 보존율"]
    # ✅ 나이와 배아 수의 비율 변수 생성
    df["배아 수 대비 나이"] = df["시술 당시 나이 숫자"] / (df["이식된 배아 수"] + 1)

    # ✅ 추가 비율 Feature 생성
    df["배아 이식 경과일 대비 나이"] = df["배아 이식 경과일"] / (df["시술 당시 나이 숫자"] + 1)


    df["난자 활용 비율"] =df["혼합된 난자 수"] / (df["수집된 신선 난자 수"]+1)



    ivf_mapping = {
    '0회': 0, '1회': 1, '2회': 2, '3회': 3, '4회': 4, '5회': 5, '6회 이상': 6
    }

    # IVF 시술 횟수 컬럼을 매핑하여 정수형으로 변환
    df["IVF 시술 횟수"] = df["IVF 시술 횟수"].map(ivf_mapping)

    df["신선 난자 대비 IVF 시술 횟수 비율"] =df["IVF 시술 횟수"] / (df["수집된 신선 난자 수"]+1)
    df["난자당 평균 혼합 횟수"] =df["혼합된 난자 수"] / (df["IVF 시술 횟수"] + 1)

    df["1~2개 이식 여부"] = (df["이식된 배아 수"].between(1, 2)).astype(int)

    df["나이 26~36 여부"] = ((df["시술 당시 나이 숫자"] >= 26) &
                      (df["시술 당시 나이 숫자"] <= 36)).astype(int)

    # 1️⃣ 이식된 배아 수 × 시술 당시 나이 숫자
    df["이식된 배아 수 × 시술 당시 나이"] = df["이식된 배아 수"] * df["시술 당시 나이 숫자"]

    # 2️⃣ 배아 이식 경과일 대비 나이 × 배아 수 대비 나이
    df["배아 이식 경과일 대비 나이 × 배아 수 대비 나이"] = df["배아 이식 경과일 대비 나이"] * df["배아 수 대비 나이"]

    # 3️⃣ 배아 수 대비 나이 / 총 생성 배아 수
    df["배아 수 대비 나이 / 총 생성 배아 수"] = df["배아 수 대비 나이"] / (df["총 생성 배아 수"] + 1)

    # 4️⃣ 이식된 배아 수 × 배아 이식 경과일 대비 나이
    df["이식된 배아 수 × 배아 이식 경과일 대비 나이"] = df["이식된 배아 수"] * df["배아 이식 경과일 대비 나이"]

    # 5️⃣ 시술 당시 나이 숫자 / 총 생성 배아 수
    df["시술 당시 나이 숫자 / 총 생성 배아 수"] = df["시술 당시 나이 숫자"] / (df["총 생성 배아 수"] + 1)

    return df



# ✅ 데이터 로드
train = pd.read_csv("./data/train.csv")
test = pd.read_csv("./data/test.csv")

train = preprocess_data(train)
test = preprocess_data(test)

# LightGBM을 위한 범주형 변수 변환
train["시술 시기 코드"] = train["시술 시기 코드"].astype("category")
test["시술 시기 코드"] = test["시술 시기 코드"].astype("category")

# ✅ ID 제거
train = train.drop(columns=["ID"])
test_id = test["ID"]
test= test.drop(columns=["ID"])

hyperparameters = {
    # ✅ GPU 지원 모델 (속도 빠르고 성능 우수)
    "GBM": {},  # LightGBM (트리 부스팅, 속도 빠름)
    "XGB": {},  # XGBoost (트리 부스팅, 강력한 성능)
    "CAT": {},
    "NN_TORCH": {},
    "FASTAI": {},

    # ✅ CPU 지원 모델 (앙상블 다양성 확보)
   "RF": {},  # Random Forest (앙상블 성능 향상)
   "XT": {}   # Extra Trees (랜덤성이 강한 트리 모델)
}

hyperparameter_tune_kwargs = {
    'num_trials': 100,
    'searcher': 'bayes',  # 베이지안 최적화 방식
    'scheduler': 'local'
}
# ✅ 모델 저장 경로
save_path = ""

# 모델 학습
predictor = TabularPredictor(label="임신 성공 여부", problem_type="binary" ,eval_metric="roc_auc",path=save_path)
predictor.fit(train, presets="best_quality",
              time_limit=60000,
              hyperparameters=hyperparameters,
              hyperparameter_tune_kwargs=hyperparameter_tune_kwargs,  # ✅ 하이퍼파라미터 튜닝 추가
              num_bag_folds=10,
              auto_stack="True",
              dynamic_stacking=False,  # DyStack 비활성화
              refit_full=True,
              calibrate=True,  # ✅ 확률값 보정 활성화,
              num_stack_levels=2
              )
# 예측
pred = predictor.predict_proba(test)  # ID 제거 후 예측
submission = pd.DataFrame({"ID": test_id, "probability": pred[1]})  # 1의 확률 사용

# 예측
pred = predictor.predict_proba(test)  # ID 제거 후 예측
submission = pd.DataFrame({"ID": test_id, "probability": pred[1]})  # 1의 확률 사용

# 결과 병합 및 저장
submission.to_csv("Submission_PG.csv", index=False)

# 2️⃣ 가장 성능이 좋은 개별 모델 가져오기 (최신 AutoGluon 방식)
best_model = predictor.model_best

# 3️⃣ 보정 전 확률값 예측 (개별 모델 사용)
pred_uncalibrated = predictor.predict_proba(test, model=best_model)

# 4️⃣ 보정 전 결과 저장
submission_uncalibrated = pd.DataFrame({
    "ID": test_id,
    "probability": pred_uncalibrated[1]  # 1 클래스의 확률
})

# 5️⃣ CSV 파일로 저장
submission_uncalibrated.to_csv("improved_ansamble_autogluonV2.csv", index=False)

print("Submission file created: Submission_uncalibrate.csv")

# 리더보드 출력
predictor.leaderboard(silent=False)

# 1. Get the individual models and their weights from the ensemble
ensemble_model = predictor._trainer.load_model(best_model)

# 2. Access the model weights through the '_get_model_weights' method
model_weights = ensemble_model._get_model_weights() # Access the weights using the method

# 3. Print the model names and their corresponding weights
print("앙상블 모델 가중치:")
for model_name, weight in model_weights.items():
    print(f"  {model_name}: {weight}")

importance = predictor.feature_importance(train)
print(importance)

importance.head(40)

importance.tail(33)

# '특정 시술 유형' 별 '임신 성공 여부' 개수 확인
success_counts = train.groupby("총 생성 배아 수")["임신 성공 여부"].value_counts().unstack().fillna(0).astype(int)

# 결과 출력
print(success_counts)
