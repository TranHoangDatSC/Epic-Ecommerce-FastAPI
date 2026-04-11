import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.models import User  # Nhớ đúng đường dẫn models của ný

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # THAY EMAIL CỦA THẰNG USER ĐANG LỖI VÀO ĐÂY
    target_email = "user1@gmail.com" 
    user = db.query(User).filter(User.email == target_email).first()
    
    if user:
        print(f"Role hiện tại của {target_email} là: {user.user_roles}")
        user.user_roles = 3  # Ép nó về 3 (User thường)
        db.commit()
        print(f"==> ĐÃ FIX: Giờ {target_email} có role_id = {user.user_roles}")
    else:
        print("Không tìm thấy thằng user này!")
except Exception as e:
    print(f"Lỗi rồi ný ơi: {e}")
finally:
    db.close()