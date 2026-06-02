import json
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from tensorflow.keras.models import load_model

# Import sequence creator from predictor
from predictor import create_sequences, TIME_STEPS


# ==========================================================
# LOAD METRICS FILE
# ==========================================================
def load_metrics(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not load metrics file: {e}")
        return None


# ==================================
# SYSTEM METRICS
# ==================================
def allocation_accuracy(total_tasks, successful_tasks):
    if total_tasks == 0:
        return 0
    return (successful_tasks / total_tasks) * 100


def sla_compliance(total_tasks, sla_violations):
    if total_tasks == 0:
        return 0
    return (1 - (sla_violations / total_tasks)) * 100


# ==========================================================
# PREDICTION METRICS (FOR LSTM - REGRESSION)
# ==========================================================
def prediction_metrics(actual, predicted):

    if len(actual) == 0 or len(predicted) == 0:
        return 0, 0, 0, 0

    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    r2 = r2_score(actual, predicted)

    # Mean Absolute Percentage Error
    actual_nonzero = np.where(actual == 0, 1e-8, actual)
    mape = np.mean(np.abs((actual - predicted) / actual_nonzero)) * 100

    return mae, rmse, r2, mape


# ==========================================================
# GET REAL LSTM PREDICTIONS (CPU PREDICTION)
# ==========================================================
def get_lstm_real_predictions(
    data_file="training_data.csv",
    model_file="lstm_model.keras",
    scaler_file="scaler.save"
):

    try:
        df = pd.read_csv(data_file)
    except Exception as e:
        print(f"[ERROR] Could not read dataset: {e}")
        return None, None

    if len(df) < TIME_STEPS + 1:
        print("[ERROR] Not enough data for evaluation.")
        return None, None

    try:
        scaler = joblib.load(scaler_file)
        model = load_model(model_file, compile=False)
    except Exception as e:
        print(f"[ERROR] Could not load model or scaler: {e}")
        return None, None

    # Scale dataset
    scaled_data = scaler.transform(df)

    # Create sequences
    X, y = create_sequences(scaled_data, TIME_STEPS)

    # Predict
    predictions = model.predict(X, verbose=0)

    # Reverse scaling (assuming CPU is first column)
    cpu_min = scaler.data_min_[0]
    cpu_max = scaler.data_max_[0]

    actual = y * (cpu_max - cpu_min) + cpu_min
    predicted = predictions.flatten() * (cpu_max - cpu_min) + cpu_min

    return actual, predicted


# ==========================================================
# GENERATE FULL RESEARCH REPORT
# ==========================================================
def generate_report(metrics_file):

    data = load_metrics(metrics_file)
    if data is None:
        return

    total_tasks = data.get("total_tasks", 0)
    successful_tasks = data.get("successful_tasks", 0)
    sla_violations = data.get("sla_violations", 0)

    alloc_acc = allocation_accuracy(total_tasks, successful_tasks)
    sla_rate = sla_compliance(total_tasks, sla_violations)

    print("\n================ SYSTEM EVALUATION REPORT ================")
    print(f"Total Tasks           : {total_tasks}")
    print(f"Successful Tasks      : {successful_tasks}")
    print(f"SLA Violations        : {sla_violations}")
    print("----------------------------------------------------------")
    print(f"Task Allocation Success Rate    : {alloc_acc:.2f}%")
    print(f"SLA Compliance Rate   : {sla_rate:.2f}%")

    # ------------------------------------------------------
    # LSTM Evaluation
    # ------------------------------------------------------
    actual, predicted = get_lstm_real_predictions()

    if actual is not None and predicted is not None:

        mae, rmse, r2, mape = prediction_metrics(actual, predicted)

        print("\n---------------- LSTM Prediction Performance -------------")
        print(f"MAE   (Mean Absolute Error)         : {mae:.4f}")
        print(f"RMSE  (Root Mean Squared Error)     : {rmse:.4f}")
        print(f"R2    (Coefficient of Determination): {r2:.4f}")
        print(f"MAPE  (Mean Abs % Error)            : {mape:.2f}%")

        # 🔎 Sample prediction check
        print("\nSample Predictions (CPU Load):")
        for i in range(min(5, len(actual))):
            print(f"Actual: {actual[i]:.2f} | Predicted: {predicted[i]:.2f}")

    print("==========================================================\n")


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":

    generate_report("metrics.json")
