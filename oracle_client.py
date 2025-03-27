# oracle_client.py (in-memory SQLite version for testing)
import sqlite3

def init_memory_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Create sample table
    cursor.execute("""
        CREATE TABLE cases_table (
            case_number TEXT PRIMARY KEY,
            case_description TEXT,
            case_comments TEXT
        )
    """)

    # Insert mock data
    cursor.executemany("""
        INSERT INTO cases_table (case_number, case_description, case_comments)
        VALUES (?, ?, ?)
    """, [
        ("123456", "System crash when exporting reports", "Issue occurs after patch update."),
        ("654321", "Login failure for admin accounts", "Likely due to expired certificates."),
        ("789012", "Data sync slow between nodes", "Observed high latency on weekends.")
    ])

    conn.commit()
    return conn

# Shared connection instance
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
        return f"{row[0]}\n{row[1]}"
    else:
        return ""