import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='123', database='oldshop')
cursor = conn.cursor()

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'user' ORDER BY ordinal_position")
columns = cursor.fetchall()

print('User table columns:')
for col in columns:
    print(f'- {col[0]}')

cursor.close()
conn.close()