import os
import psycopg2
import time
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123")
DB_NAME = os.getenv("DB_NAME", "oldshop")

def setup_db():
    print("\n" + "="*60)
    print("   FINAL DATABASE ENGINE - HANDLING TRIGGERS & SEEDS")
    print("="*60)

    # 1. Chờ Server và tạo DB
    while True:
        try:
            conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname="postgres", connect_timeout=2)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
            if not cur.fetchone():
                print(f"[INFO] Creating database: {DB_NAME}")
                cur.execute(f"CREATE DATABASE {DB_NAME}")
            cur.close()
            conn.close()
            break
        except Exception as e:
            print(f"[WAIT] Waiting for Postgres Server...")
            time.sleep(2)

    # 2. Kết nối vào DB chính
    try:
        # Quan trọng: Mở kết nối với Autocommit = False để kiểm soát Transaction cho Trigger
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
        cur = conn.cursor()
        
        # FIX LỖI gen_salt: Cài extension pgcrypto ngay lập tức
        print("[INIT] Installing extensions...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        conn.commit()

        base_path = "/database_src"
        steps = ["01_schema", "02_functions", "03_seeds", "04_modules"]

        for step in steps:
            target_dir = os.path.join(base_path, step)
            if not os.path.exists(target_dir):
                continue

            print(f"\n>>> NẠP BƯỚC: {step}")
            
            # Duyệt sâu mọi folder con
            for root, dirs, files in os.walk(target_dir):
                for file in sorted(files):
                    if file.endswith(".sql"):
                        # Né các file gây nhiễu
                        if "init.sql" in file or "all_functions.sql" in file or "_old" in file:
                            continue
                        
                        sql_path = os.path.join(root, file)
                        print(f" [EXEC] -> {file} (Path: {os.path.relpath(sql_path, base_path)})")
                        
                        try:
                            with open(sql_path, 'r', encoding='utf-8') as f:
                                sql_content = f.read()
                                if sql_content.strip():
                                    # Thực thi nội dung file SQL
                                    cur.execute(sql_content)
                            conn.commit() # Lưu lại sau mỗi file thành công
                        except Exception as sql_err:
                            conn.rollback() # Nếu file lỗi, rollback lại trạng thái trước file đó
                            # In lỗi chi tiết để Hoang soi
                            print(f" [LỖI SQL] Tại {file}: {str(sql_err).strip()}")

        cur.close()
        conn.close()
        print("\n" + "="*60)
        print("   CHỐT SỔ: TRÁI TIM ĐÃ ĐẬP, DATA ĐÃ ĐỦ!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"[FATAL] System failed: {e}")

if __name__ == "__main__":
    setup_db()