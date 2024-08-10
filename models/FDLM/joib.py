import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# CSV 파일 읽기
df1 = pd.read_csv('financial_data1.csv')
df2 = pd.read_csv('financial_data2.csv')

# 데이터 병합 및 전처리
merged_df = pd.concat([df1, df2]).dropna().reset_index(drop=True)

# 특징(X)과 타겟(y) 분리 (예시로, 'feature'와 'target'이라는 열이 있다고 가정)
X = merged_df[['feature1', 'feature2']]  # 예시
y = merged_df['target']  # 예시

# 모델 학습
model = LinearRegression()
model.fit(X, y)

# 학습된 모델을 파일로 저장
joblib.dump(model, 'financial_model.pkl')

# 저장된 모델 불러오기.
model = joblib.load('financial_model.pkl')

# 모델을 사용하여 예측 수행
new_data = [[5, 3]]  # 예시 데이터
prediction = model.predict(new_data)

print(prediction)