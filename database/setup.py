import os
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Lấy thông tin từ biến môi trường (Docker sẽ truyền vào) hoặc dùng default
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123")
DB_NAME = os.getenv("DB_NAME", "oldshop")

def wait_for_db():
    """Đợi cho đến khi database sẵn sàng kết nối"""
    print(f"[INFO] Đang kiểm tra kết nối tới {DB_HOST}:{DB_PORT}...")
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname="postgres" # Kết nối vào db mặc định trước
            )
            conn.close()
            print("[OK] Đã kết nối được tới PostgreSQL Server.")
            return True
        except Exception as e:
            print(f"[WAIT] Server chưa sẵn sàng... ({retries} lần thử lại)")
            retries -= 1
            time.sleep(3)
    return False

def create_database():
    """Tạo database nếu chưa tồn tại"""
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    exists = cur.fetchone()
    if not exists:
        print(f"[INFO] Đang tạo database: {DB_NAME}")
        cur.execute(f"CREATE DATABASE {DB_NAME}")
    else:
        print(f"[INFO] Database '{DB_NAME}' đã tồn tại.")
    
    cur.close()
    conn.close()

def run_sql_file(file_path):
    """Thực thi file SQL"""
    if not os.path.exists(file_path):
        print(f"[ERROR] Không tìm thấy file: {file_path}")
        return

    print(f"[INFO] Đang thực thi: {file_path}")
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
        cur = conn.cursor()
        with open(file_path, 'r', encoding='utf-8') as f:
            cur.execute(f.read())
        conn.commit()
        cur.close()
        conn.close()
        print(f"[OK] Hoàn thành: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"[ERROR] Lỗi khi chạy file {file_path}: {e}")

if __name__ == "__main__":
    if wait_for_db():
        create_database()
        
        # Đường dẫn tới thư mục database dựa trên cấu trúc của bạn
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Chạy file init.sql tổng hợp hoặc chạy theo thứ tự thư mục
        init_script = os.path.join(base_dir, "init.sql")
        
        if os.path.exists(init_script):
            run_sql_file(init_script)
        else:
            # Nếu không có file tổng, chạy lần lượt các folder theo cấu trúc của bạn
            folders = ["01_schema", "02_functions", "03_seeds", "04_modules"]
            for folder in folders:
                folder_path = os.path.join(base_dir, folder)
                if os.path.isdir(folder_path):
                    for sql_file in sorted(os.listdir(folder_path)):
                        if sql_file.endswith(".sql"):
                            run_sql_file(os.path.join(folder_path, sql_file))
        
        print("\n[SUCCESS] Hệ thống database đã sẵn sàng cho Oldshop!")
    else:
        print("[FAIL] Không thể kết nối tới Database Server. Thoát...")
        exit(1)