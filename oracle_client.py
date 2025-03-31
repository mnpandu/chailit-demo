# oracle_client.py (extended for claims)
import sqlite3
import pandas as pd

def init_memory_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create case table
    cursor.execute("""
        CREATE TABLE cases_table (
            case_number TEXT PRIMARY KEY,
            case_description TEXT,
            case_comments TEXT
        )
    """)

    cursor.executemany("""
        INSERT INTO cases_table (case_number, case_description, case_comments)
        VALUES (?, ?, ?)
    """, [
        ("MR123456", "System crash when exporting reports", "Issue occurs after patch update."),
        ("MR654321", "Login failure for admin accounts", "Likely due to expired certificates."),
        ("MR789012", "Data sync slow between nodes", "Observed high latency on weekends."),
    ])

    # Create claims table
    cursor.execute("""
        CREATE TABLE claims_table (
            claim_number TEXT PRIMARY KEY,
            case_number TEXT,
            base_rate INTEGER,
            units INTEGER,
            discount INTEGER,
            calculated_amount INTEGER,
            expected_amount INTEGER,
            FOREIGN KEY (case_number) REFERENCES cases_table(case_number)
        )
    """)

    cursor.executemany("""
        INSERT INTO claims_table (claim_number, case_number, base_rate, units, discount, calculated_amount, expected_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        ("CL123456", "456789", 100, 3, 50, 250, 300),
        ("CL654321", "123456", 80, 5, 20, 380, 380),
        ("CL789012", "654321", 120, 2, 0, 360, 240),
        ("CL789013", "789012", 90, 4, 30, 330, 360),
    ])

    conn.commit()
    return conn

DB_CONN = init_memory_db()

def fetch_case_data(case_number: str) -> str:
    cursor = DB_CONN.cursor()
    cursor.execute("""
        SELECT case_description, case_comments
        FROM cases_table
        WHERE case_number = ?
    """, (case_number,))
    row = cursor.fetchone()
    if row:
        return f"{row[0]} {row[1]}"
    else:
        return ""
    
def fetch_claim_data(claim_number: str) -> str:
    cursor = DB_CONN.cursor()
    cursor.execute("""
        SELECT base_rate, units, discount, calculated_amount, expected_amount
        FROM claims_table
        WHERE claim_number = ?
    """, (claim_number,))
    row = cursor.fetchone()
    if row:
        return (
            f"{row[0]} {row[1]} {row[2]} {row[3]} {row[4]}"
        )
    return ""

def get_claims_data() -> pd.DataFrame:
    query = "SELECT * FROM claims_table"
    return pd.read_sql(query, DB_CONN)
