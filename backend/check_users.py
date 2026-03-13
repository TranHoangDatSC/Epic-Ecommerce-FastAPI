import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='123', database='oldshop')
cursor = conn.cursor()

cursor.execute('SELECT user_id, username, email FROM "user" LIMIT 5')
users = cursor.fetchall()

print('Users in database:')
if users:
    for user in users:
        print(f'ID: {user[0]}, Username: {user[1]}, Email: {user[2]}')
else:
    print('No users found in database')

cursor.close()
conn.close()