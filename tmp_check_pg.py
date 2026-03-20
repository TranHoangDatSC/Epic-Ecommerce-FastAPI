import psycopg2
from psycopg2 import Error

try:
    connection = psycopg2.connect(user="postgres",
                                  password="123",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="oldshop")

    cursor = connection.cursor()
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'product'")
    columns = cursor.fetchall()
    print("Columns in product table:")
    for col in columns:
        print(col[0])

    if any("transfer" in c[0].lower() for c in columns):
        print("\nFound transfer_method (or similar)!")

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
