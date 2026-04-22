import joblib
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "fraud_model.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.joblib")
from datetime import datetime

def verify_transaction_ml(amount, old_balance):
    try:
        amount_f = float(amount)
        # RULE 1: Cứng - Trên 100tr là gậy đỏ
        if amount_f > 100_000_000:
            return {"is_fraud": True, "score": 1.0, "reason": "High amount limit exceeded"}

        # RULE 2: Thời gian nhạy cảm (ví dụ 1h - 4h sáng)
        current_hour = datetime.now().hour
        time_risk = 0.4 if (1 <= current_hour <= 4) else 0.0

        # ML LOGIC
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        # Thêm delta (số dư còn lại) để model học tính logic của tài khoản
        features = np.array([[amount_f, float(old_balance), float(old_balance) - amount_f]])
        features_scaled = scaler.transform(features)
        
        raw_score = model.decision_function(features_scaled)[0]
        ml_score = round(float(min(1.0, abs(raw_score) * 5)), 4)
        
        # HYBRID SCORE: Kết hợp ML và Rule thời gian
        final_score = min(1.0, ml_score + time_risk)
        
        # Ngưỡng 0.5 là bắt đầu bắt đợi 1 phút (Bẫy tâm lý)
        # Ngưỡng 0.8 là chặn hoàn toàn
        return {
            "is_fraud": final_score > 0.8, 
            "is_suspicious": final_score > 0.5, 
            "score": final_score
        }
    except:
        return {"is_fraud": False, "is_suspicious": False, "score": 0.0}