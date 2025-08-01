import sqlite3
from pathlib import Path

DB_PATH = Path("data/policies.db")

# Ensure data folder exists
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employer_number TEXT,
                employer_name TEXT,
                member_number TEXT,
                member_name TEXT,
                id_number TEXT,
                period_start TEXT,
                period_end TEXT,
                received_date TEXT,
                compliance_officer_date TEXT,
                branch_manager_date TEXT,
                cash_office_date TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_id INTEGER,
                contribution_month TEXT,
                amount REAL,
                FOREIGN KEY(policy_id) REFERENCES policies(id)
            )
        ''')
        conn.commit()

def get_connection():
    return sqlite3.connect(DB_PATH)