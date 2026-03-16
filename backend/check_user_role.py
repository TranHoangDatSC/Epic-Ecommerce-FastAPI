import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='123', database='oldshop')
cursor = conn.cursor()

cursor.execute('SELECT u.user_id, u.username, ur.role_id, r.role_name FROM "user" u JOIN user_role ur ON u.user_id = ur.user_id JOIN role r ON ur.role_id = r.role_id WHERE u.user_id = 3')
result = cursor.fetchone()

print(f'User 3: ID={result[0]}, Username={result[1]}, Role ID={result[2]}, Role Name={result[3]}')

cursor.close()
conn.close()