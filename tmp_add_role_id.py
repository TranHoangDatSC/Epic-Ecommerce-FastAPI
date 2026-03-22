import psycopg2
from psycopg2 import Error

try:
    connection = psycopg2.connect(user="postgres",
                                  password="123",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="oldshop")

    cursor = connection.cursor()
    # Add role_id column
    cursor.execute('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS role_id INT DEFAULT 3 REFERENCES role(role_id);')
    connection.commit()
    print("Added role_id column to user table")

    # Update existing users
    cursor.execute('''
        UPDATE "user" SET role_id = (
            SELECT role_id FROM user_role WHERE user_role.user_id = "user".user_id LIMIT 1
        ) WHERE role_id = 3 OR role_id IS NULL;
    ''')
    connection.commit()
    print("Updated existing users with role_id")

except (Exception, Error) as error:
    print("Error:", error)
finally:
    if connection:
        cursor.close()
        connection.close()