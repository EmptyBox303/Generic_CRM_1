import sqlite3

try:
    with sqlite3.connect("sql.db") as db:
        print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
except sqlite3.OperationalError as e:
    print("Failed to open database:", e)

cur = db.cursor()
try:
    with open("org_setup.sql") as file:
        db_setup_sql = ''.join(file.readlines())
except Exception as e:
    print(f"An error occurred: {e}")


cur.executescript(db_setup_sql)
db.commit()

