import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

MODEL_FILE = "lstm_model.keras"
SCALER_FILE = "scaler.save"
DATA_FILE = "training_data.csv"

TIME_STEPS = 5


# -----------------------------------------
# Log data (called every prediction)
# -----------------------------------------
def log_training_data(vm_metrics):
    data = {
        "cpu": vm_metrics.get("cpu", 0),
        "memory": vm_metrics.get("memory", 0),
        "network": vm_metrics.get("network", 0),
        "tasks": vm_metrics.get("tasks", 0)
    }

    df = pd.DataFrame([data])

    if not os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, index=False)
    else:
        df.to_csv(DATA_FILE, mode='a', header=False, index=False)


# -----------------------------------------
# Create LSTM sequences
# -----------------------------------------
def create_sequences(data, time_steps=5):
    X, y = [], []

    for i in range(len(data) - time_steps):
        X.append(data[i:i + time_steps])
        y.append(data[i + time_steps][0])  # CPU only

    return np.array(X), np.array(y)


# -----------------------------------------
# Train model
# -----------------------------------------
def train_model():

    if not os.path.exists(DATA_FILE):
        return None

    df = pd.read_csv(DATA_FILE)

    if len(df) < 50:
        return None

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df)

    X, y = create_sequences(scaled_data, TIME_STEPS)

    model = Sequential()
    model.add(LSTM(64, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")

    early_stop = EarlyStopping(
        patience=5,
        restore_best_weights=True
    )

    model.fit(
        X, y,
        epochs=30,
        batch_size=8,
        verbose=0,
        callbacks=[early_stop]
    )

    predictions = model.predict(X, verbose=0)

    print("\n[LSTM MODEL PERFORMANCE]")
    print("R2 :", r2_score(y, predictions))
    print("MAE:", mean_absolute_error(y, predictions))
    print("RMSE:", np.sqrt(mean_squared_error(y, predictions)))

    model.save(MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)

    return model


# -----------------------------------------
# Load model
# -----------------------------------------
def load_lstm():
    if os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE):
        model = load_model(MODEL_FILE, compile=False)
        scaler = joblib.load(SCALER_FILE)
        return model, scaler
    return None, None


# -----------------------------------------
# Predict load
# -----------------------------------------
def predict_load(vm_metrics):

    log_training_data(vm_metrics)

    model, scaler = load_lstm()

    if model is None:
        model = train_model()
        model, scaler = load_lstm()

    if model is None:
        # Safe fallback formula
        return (
            0.5 * vm_metrics.get("cpu", 0)
            + 0.3 * vm_metrics.get("memory", 0)
            + 0.2 * vm_metrics.get("tasks", 0)
        )

    df = pd.read_csv(DATA_FILE)

    if len(df) < TIME_STEPS:
        return vm_metrics.get("cpu", 0)

    scaled_data = scaler.transform(df)

    last_sequence = scaled_data[-TIME_STEPS:]
    last_sequence = np.expand_dims(last_sequence, axis=0)

    prediction = model.predict(last_sequence, verbose=0)[0][0]

    # Reverse scaling (CPU only)
    cpu_min = scaler.data_min_[0]
    cpu_max = scaler.data_max_[0]
    prediction = prediction * (cpu_max - cpu_min) + cpu_min

    # Clamp output (CRITICAL FIX)
    prediction = max(0, prediction)
    prediction = min(100, prediction)

    return float(prediction)
