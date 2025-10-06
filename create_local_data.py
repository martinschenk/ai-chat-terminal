#!/usr/bin/env python3
"""
Create new local_data table - KISS v10.0.0
Ultra-simple: nur 3 Felder!
"""

import sqlite3
import os

def create_local_data_table(db_path):
    """Create the new simple local_data table"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create new table (if not exists)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS local_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            content TEXT NOT NULL
        )
    """)

    # Create index for faster searches
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_local_data_timestamp
        ON local_data(timestamp)
    """)

    conn.commit()
    conn.close()

    print("✅ local_data table created!")

if __name__ == "__main__":
    # Test DB path
    db_path = os.path.expanduser("~/.aichat/memory.db")
    create_local_data_table(db_path)

    # Verify
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(local_data)")
    columns = cursor.fetchall()

    print("\n📊 Table Structure:")
    for col in columns:
        print(f"  {col[1]:15} {col[2]:10}")

    conn.close()
