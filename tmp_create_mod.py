import psycopg2
conn = psycopg2.connect(user='postgres', password='123', host='127.0.0.1', port='5432', database='oldshop')
cursor = conn.cursor()
cursor.execute("INSERT INTO \"user\" (username, email, password_hash, full_name, role_id, random_key) VALUES (%s, %s, %s, %s, %s, %s)", ('mod2', 'mod2@gmail.com', '$2b$12$examplehash', 'Moderator 2', 2, 'mod2'))
conn.commit()
cursor.close()
conn.close()
print('Created moderator user')