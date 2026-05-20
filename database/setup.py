import os
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Lấy thông tin từ biến môi trường (Docker truyền vào)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123")
DB_NAME = os.getenv("DB_NAME", "oldshop")

def wait_for_db():
    """Đợi cho đến khi database sẵn sàng kết nối"""
    print(f"[INFO] Đang kiểm tra kết nối tới {DB_HOST}:{DB_PORT}...")
    retries = 15
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname="postgres"
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
        print(f"[INFO] Đang tạo database '{DB_NAME}'...")
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"[OK] Đã tạo database '{DB_NAME}'.")
    else:
        print(f"[INFO] Database '{DB_NAME}' đã tồn tại.")
        
    cur.close()
    conn.close()

def run_sql_file(file_path):
    """Chạy trực tiếp 1 file SQL"""
    if not os.path.exists(file_path):
        print(f"[WARNING] Bỏ qua, không tìm thấy file: {file_path}")
        return
        
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
        cur = conn.cursor()
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            # Bỏ qua nếu file rỗng
            if sql_content.strip():
                cur.execute(sql_content)
        conn.commit()
        cur.close()
        conn.close()
        print(f"[OK] Đã nạp thành công: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"[ERROR] Lỗi khi nạp file {os.path.basename(file_path)}: {e}")

if __name__ == "__main__":
    if wait_for_db():
        create_database()
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        init_script = os.path.join(base_dir, "init.sql")
        
        # BÍ KÍP CHỖ NÀY: Dạy Python cách hiểu lệnh \i của init.sql
        if os.path.exists(init_script):
            print(f"[INFO] Đang đọc cấu trúc từ {init_script}...")
            with open(init_script, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Chỉ lấy những dòng bắt đầu bằng \i (bỏ qua comment --)
                    if line.startswith("\\i "):
                        # Tách lấy đường dẫn (vd: 01_schema/roles.sql)
                        rel_path = line.replace("\\i ", "").strip().strip(";'\"")
                        # Đảm bảo đường dẫn chuẩn trên cả Win/Linux (Docker)
                        rel_path = rel_path.replace("/", os.sep)
                        full_path = os.path.join(base_dir, rel_path)
                        
                        run_sql_file(full_path)
            
            print("[SUCCESS] ==============================================")
            print("[SUCCESS] DATABASE ĐÃ ĐƯỢC KHỞI TẠO VÀ SẴN SÀNG SỬ DỤNG!")
            print("[SUCCESS] ==============================================")
        else:
            print("[ERROR] Không tìm thấy file init.sql!")