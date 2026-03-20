import sqlite3

db_path = r'c:\Users\hoang\Downloads\Web Technology\Oldshop-Ecommecre\oldshop.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('PRAGMA table_info("product")')
columns = cursor.fetchall()
for col in columns:
    print(col)

conn.close()
