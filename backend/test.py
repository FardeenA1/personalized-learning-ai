from database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
INSERT INTO users(full_name, email, password)
VALUES (?, ?, ?)
""", (
    "Test User",
    "test@example.com",
    "123456"
))

conn.commit()

print("Inserted successfully!")

conn.close()