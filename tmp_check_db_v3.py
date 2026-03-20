import sqlite3

db_path = r'c:\Users\hoang\Downloads\Web Technology\Oldshop-Ecommecre\oldshop.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    t_name = table[0]
    cursor.execute(f'PRAGMA table_info("{t_name}")')
    cols = cursor.fetchall()
    for col in cols:
        if "transfer" in col[1].lower() or "method" in col[1].lower():
            print(f"Table: {t_name}, Column: {col[1]}")

conn.close()
