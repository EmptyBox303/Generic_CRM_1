import sqlite3

try:
    with sqlite3.connect("sql.db") as db:
        print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
except sqlite3.OperationalError as e:
    print("Failed to open database:", e)

cur = db.cursor()

