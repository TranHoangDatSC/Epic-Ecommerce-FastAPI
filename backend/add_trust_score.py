import psycopg2

# Database connection
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    user='postgres',
    password='123',
    database='oldshop'
)
cursor = conn.cursor()

try:
    # Check if trust_score column exists
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'user' AND column_name = 'trust_score'
    """)

    if cursor.fetchone():
        print('✓ trust_score column already exists')
    else:
        # Add trust_score column
        cursor.execute('ALTER TABLE "user" ADD COLUMN trust_score DECIMAL(5,2) DEFAULT 0.0 NULL')
        conn.commit()
        print('✓ Added trust_score column to user table')

        # Add comment
        cursor.execute("COMMENT ON COLUMN \"user\".trust_score IS 'Trust score for sellers (role_id=3) behavior monitoring (default 0.0, nullable for non-sellers)'")
        conn.commit()
        print('✓ Added comment to trust_score column')

except Exception as e:
    print(f'✗ Error: {e}')
    conn.rollback()
finally:
    cursor.close()
    conn.close()