import sqlite3

db_path = r'c:\Users\hoang\Downloads\Web Technology\Oldshop-Ecommecre\oldshop.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    table_name = table[0]
    print(f"\nTable: {table_name}")
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    info = cursor.fetchall()
    for col in info:
        print(f"  {col[1]} ({col[2]})")

conn.close()
