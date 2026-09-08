import sqlite3

conn = sqlite3.connect("learning_assistant.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
    conn.commit()
    print("Migration successful: is_admin column added.")
except sqlite3.OperationalError as e:
    print("Migration skipped:", e)

conn.close()