import sqlite3

email = input("Enter the email to make admin: ").strip()

conn = sqlite3.connect("learning_assistant.db")
cursor = conn.cursor()

cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
conn.commit()

print(f"Updated {cursor.rowcount} row(s).")
conn.close()