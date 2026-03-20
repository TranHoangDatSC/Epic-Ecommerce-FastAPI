import sqlite3

db_path = r'c:\Users\hoang\Downloads\Web Technology\Oldshop-Ecommecre\oldshop.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def get_table_info(table_name):
    # Escape table name if it's a reserved keyword
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    return cursor.fetchall()

tables = ['user', 'role', 'category', 'product', 'order', 'order_detail', 'shopping_cart', 'shopping_cart_item']
for table in tables:
    print(f"\nTable: {table}")
    info = get_table_info(table)
    for col in info:
        print(f"  {col[1]} ({col[2]})")

conn.close()
