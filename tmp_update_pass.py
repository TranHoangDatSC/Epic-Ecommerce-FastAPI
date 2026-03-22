import psycopg2
conn = psycopg2.connect(user='postgres', password='123', host='127.0.0.1', port='5432', database='oldshop')
cursor = conn.cursor()
cursor.execute("UPDATE \"user\" SET password_hash = %s WHERE username = %s", ('$2b$12$examplehash', 'mod2'))
conn.commit()
cursor.close()
conn.close()
print('Updated password')