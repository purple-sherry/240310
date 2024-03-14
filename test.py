import pyupbit
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.metrics import mean_squared_error

dl_interval = "day"
dl_count = 1440

coin = "BTC"

dt_hours_open = pd.DataFrame()

def create_dataset(data, time_step):
    X, y = [], []
    for i in range(len(data) - time_step):
        X.append(data[i:(i + time_step)])
        y.append(data[i + time_step])
    return np.array(X), np.array(y)


ohlcv_name = "KRW-BTC"
dt_hours = pyupbit.get_ohlcv(ohlcv_name, interval=dl_interval, count=dl_count)
dt_hours_open[coin] = dt_hours['open']

    # 2차원 배열로 변환
data = dt_hours_open[coin].values.reshape(-1, 1)

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

    # 데이터 분할
train_size = int(len(scaled_data) * 0.9)
train_data = scaled_data[:train_size]
test_data = scaled_data[train_size:]

time_step = 60  # 시계열 데이터를 위한 시간 단계 설정

X_train, y_train = create_dataset(train_data, time_step)
X_test, y_test = create_dataset(test_data, time_step)

    # LSTM 모델 정의
model = Sequential()
model.add(LSTM(units=200, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(LSTM(units=200, return_sequences=False))
model.add(Dense(units=1))
model.compile(optimizer='adam', loss='mean_squared_error')

    # 모델 학습
history = model.fit(X_train, y_train, epochs=100, batch_size=64, validation_data=(X_test, y_test), verbose=1)

    # 검증 데이터에 대한 예측
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)

    # 예측 결과 시각화
plt.figure(figsize=(10, 6))
plt.plot(dt_hours_open.index[train_size + time_step:], dt_hours_open.iloc[train_size + time_step:], label='Actual')
plt.plot(dt_hours_open.index[train_size + time_step:], predictions, label='Predicted')
plt.legend()
plt.show()
    
# 1시간 뒤의 가격을 예측하는 함수
def predict_next_hour_price(model, test_X, scaler):
    # 최신 데이터 가져오기
    latest_data = test_X[-1].reshape(1, test_X.shape[1], test_X.shape[2])
    # 다음 시간 간격의 가격 예측
    next_hour_prediction = model.predict(latest_data)
    # 스케일링 역변환
    next_hour_prediction = scaler.inverse_transform(next_hour_prediction)
    return next_hour_prediction

# 모델 평가 및 1시간 뒤 가격 예측
def evaluate_model_and_predict_next_hour_price(model, test_X, test_y, scaler):
    # 모델 평가
    rmse = model.evaluate(test_X, test_y, verbose=0)
    print(f'Model Evaluation - RMSE: {rmse}')
    
    # 1시간 뒤 가격 예측
    next_hour_prediction = predict_next_hour_price(model, test_X, scaler)
    print(f'Next Hour Prediction: {int(next_hour_prediction)}')

# 모델 평가 및 1시간 뒤 가격 예측 실행
evaluate_model_and_predict_next_hour_price(model, X_test, y_test, scaler)

