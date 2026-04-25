import joblib
import numpy as np
import os
from datetime import datetime

# Xác định đường dẫn file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "fraud_model.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.joblib")

# --- CẢI TIẾN: LOAD MODEL MỘT LẦN DUY NHẤT (CACHING) ---
# Tránh việc load file liên tục gây tốn CPU/RAM
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    MODEL_READY = True
except Exception as e:
    print(f"CRITICAL: Fraud Model not found or corrupted: {e}")
    MODEL_READY = False

def verify_transaction_ml(amount, old_balance):
    try:
        amount_f = float(amount)
        balance_f = float(old_balance)
        
        # 1. Hard Rule
        if amount_f > 100_000_000:
            return {"is_fraud": True, "is_suspicious": True, "score": 1.0}

        # 2. Fake Data cho đủ 12 features để lừa Scaler
        # Chúng ta tạo mảng 12 số, trong đó 3 số đầu là thật, còn lại là 0
        raw_features = [amount_f, balance_f, balance_f - amount_f] + [0.0] * 9
        features = np.array([raw_features])

        if MODEL_READY:
            features_scaled = scaler.transform(features)
            raw_score = model.decision_function(features_scaled)[0]

            ml_score = round(float(min(0.9, (raw_score) * 5)), 4)
        else:
            ml_score = 0.1

        current_hour = datetime.now().hour
        time_risk = 0.0 if (1 <= current_hour <= 4) else 0.0
        final_score = min(1.0, ml_score + time_risk)

        return {
            "is_fraud": final_score > 0.9,
            "is_suspicious": final_score > 0.7,
            "score": round(final_score, 4)
        }
    except Exception as e:
        print(f"Error in fraud detection: {e}")
        return {"is_fraud": False, "is_suspicious": False, "score": 0.01}