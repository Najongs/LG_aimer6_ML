# 🤖 난임 환자 대상 임신 성공 여부 예측 AI 모델 개발

## 📋 프로젝트 개요
난임은 전 세계적으로 증가하는 중요한 의료 문제로, 많은 부부들이 신체적·정신적 부담을 겪고 있습니다.  
본 프로젝트는 **AI 기반 예측 모델**을 활용하여 난임 치료 과정에서 **임신 성공 여부**를 예측하고, 주요 **결정 요인(Feature)을 탐색**하는 것을 목표로 합니다.  
이를 통해 환자의 시술 부담을 줄이고 맞춤형 치료 계획을 수립할 수 있는 솔루션을 제시합니다.

---

## 🚀 주요 목표
- **임신 성공 여부 예측 모델** 개발
- **임신 성공에 영향을 미치는 주요 특성 도출**
- **최적의 AI 모델을 탐색하고 성능 비교**
- **Stacking 앙상블 기법을 통한 예측 성능 향상**

---

## 📊 사용한 데이터
난임 환자 데이터는 **카테고리형** 및 **수치형 변수**로 구성되어 있으며, 다음과 같은 주요 변수가 포함되어 있습니다.

### 주요 변수
- **수치형 변수 (Numeric Features)**
  - 임신 시도 또는 마지막 임신 경과 연수
  - 총 생성 배아 수
  - 미세주입된 난자 수
  - 이식된 배아 수
  - 난자 채취 경과일, 배아 이식 경과일 등

- **카테고리형 변수 (Categorical Features)**
  - 시술 유형
  - 특정 시술 유형
  - 남성/여성 불임 원인
  - 배란 자극 여부, 단일 배아 이식 여부, 착상 전 유전 검사 여부 등

---

## 🛠️ 사용한 기술 및 모델

### 📦 주요 라이브러리
- **pandas, numpy**: 데이터 전처리
- **scikit-learn**: 데이터 분할, 모델 학습 및 교차 검증
- **LightGBM, XGBoost**: 주요 예측 모델
- **imblearn (SMOTE + Tomek)**: 데이터 불균형 처리
- **matplotlib**: 시각화
- **StackingClassifier**: 앙상블 기법

---

## ⚙️ 코드 흐름

### **1. 데이터 전처리**
- 결측값 처리 및 카테고리형 변수를 **OrdinalEncoder**로 변환
- **수치형 변수는 StandardScaler**로 정규화
- **데이터 불균형 문제** 해결을 위해 **SMOTETomek** 기법 적용
- **Feature Selection**: `SelectKBest`를 활용하여 상위 50개의 중요한 변수를 선택

### **2. 모델 학습 및 하이퍼파라미터 튜닝**
#### **LightGBM**
- `GridSearchCV`를 사용해 최적의 하이퍼파라미터 탐색  
- **최적 파라미터**:  
  ```python
  {'learning_rate': 0.01, 'max_depth': -1, 'n_estimators': 1000, 'num_leaves': 70}

#### **XGBoost**
- `GridSearchCV`를 사용해 최적의 하이퍼파라미터 탐색  
- **최적 파라미터**:  
  ```python
  {'colsample_bytree': 0.8, 'gamma': 0, 'learning_rate': 0.05, 'max_depth': 7, 'n_estimators': 300, 'subsample': 0.8}

### **3. Stacking 앙상블**
- stackingClassifier를 사용해 LightGBM, XGBoost를 기반 모델로 활용하고, 최종 메타 모델로 Logistic Regression을 적용
- 교차 검증 (5-Fold Cross Validation)**을 통해 각 모델의 ROC-AUC 점수 비교

### **4. 최종 제출 파일 생성**
- Stacking 앙상블 모델을 사용해 테스트 데이터에 대한 예측 확률 생성
- 제출 파일 (stacking_ensemble_submit.csv) 저장

### Ref
- 데이터 전처리 과정에서 결측값 처리는 0으로 대체했으며, 카테고리형 변수는 Ordinal Encoding을 적용했습니다.
- 데이터 불균형을 해결하기 위해 SMOTETomek 기법을 사용하였습니다.
