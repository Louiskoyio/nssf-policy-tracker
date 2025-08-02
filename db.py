import sqlite3
from pathlib import Path


DB_PATH = Path("data/policies.db")

# Ensure data folder exists
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Existing tables
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

        # NEW: Table for uploaded schedules
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_number TEXT NOT NULL,
                member_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # NEW: Table for schedule tracking stages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER NOT NULL,
                stage TEXT NOT NULL,  -- 'Compliance Officer', 'Branch Manager', 'Accountant'
                entered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                exited_at TIMESTAMP,
                duration_days REAL,
                handled_by TEXT,
                FOREIGN KEY(schedule_id) REFERENCES schedules(id)
            )
        ''')
        

        conn.commit()

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access
    return conn


init_db()

