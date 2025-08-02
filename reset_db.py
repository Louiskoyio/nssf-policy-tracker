import sqlite3
from pathlib import Path


DB_PATH = Path("data/policies.db")

def reset_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        tables = [
            "contributions",
            "policies"
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")  # Reset autoincrement IDs
        conn.commit()
        print("All data cleared.")

if __name__ == "__main__":
    reset_database()