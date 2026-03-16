import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='123', database='oldshop')
cursor = conn.cursor()

cursor.execute('SELECT * FROM user_role')
results = cursor.fetchall()

print('User roles:')
for r in results:
    print(f'User ID: {r[0]}, Role ID: {r[1]}')

cursor.close()
conn.close()