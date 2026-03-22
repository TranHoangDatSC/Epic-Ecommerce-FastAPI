import psycopg2
conn = psycopg2.connect(user='postgres', password='123', host='127.0.0.1', port='5432', database='oldshop')
cursor = conn.cursor()
cursor.execute('UPDATE "user" SET role_id = 1 WHERE user_id = 3')
conn.commit()
cursor.close()
conn.close()
print('Updated user 3 to role_id=1')