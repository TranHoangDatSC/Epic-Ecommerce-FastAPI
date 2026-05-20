import os
import time
import psycopg2
import subprocess
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123")
DB_NAME = os.getenv("DB_NAME", "oldshop")

def wait_for_db():
    print(f"[INFO] Đang kiểm tra kết nối tới {DB_HOST}:{DB_PORT}...")
    retries = 15
    while retries > 0:
        try:
            conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname="postgres")
            conn.close()
            print("[OK] PostgreSQL Server đã sẵn sàng.")
            return True
        except:
            print(f"[WAIT] Đợi DB khởi động... ({retries} lần thử)")
            retries -= 1
            time.sleep(3)
    return False

def init_db():
    # Tạo Database nếu chưa có
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    if not cur.fetchone():
        print(f"[INFO] Đang tạo database '{DB_NAME}'...")
        cur.execute(f"CREATE DATABASE {DB_NAME}")
    cur.close()
    conn.close()

def run_init_script_with_psql():
    """Dùng lệnh psql gốc để chạy file init.sql giống hệt như setup.cmd"""
    base_dir = "/database_src" if os.path.exists("/database_src") else os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../database"))
    init_script = os.path.join(base_dir, "init.sql")
    
    if not os.path.exists(init_script):
        print(f"[ERROR] Không tìm thấy file mục lục tại: {init_script}")
        return

    print(f"[INFO] Đang nhờ 'psql' chạy file: {init_script}")
    
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    try:
        subprocess.run(
            ["psql", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, "-d", DB_NAME, "-f", init_script],
            env=env,
            check=True,
            cwd=base_dir  # <--- BÍ KÍP CHÍNH LÀ DÒNG NÀY: Ép nó đứng ở /database_src để chạy
        )
        print("\n[SUCCESS] ==============================================")
        print("[SUCCESS] PSQL ĐÃ NẠP DỮ LIỆU THÀNH CÔNG 100%!")
        print("[SUCCESS] ==============================================")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Quá trình chạy psql thất bại: {e}")

if __name__ == "__main__":
    if wait_for_db():
        init_db()
        run_init_script_with_psql()