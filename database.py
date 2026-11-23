import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).with_name("smarthairscan.db")

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspected_at TEXT NOT NULL,
                student_id TEXT NOT NULL,
                student_name TEXT NOT NULL,
                student_class TEXT NOT NULL,
                long_hair TEXT NOT NULL,
                colored_hair TEXT NOT NULL,
                color_note TEXT,
                ai_notes TEXT,
                reviewer TEXT
            )
        """)
        conn.commit()

def add_inspection(student_id, student_name, student_class,
                   long_hair, colored_hair, color_note="", ai_notes="", reviewer=""):
    with connect() as conn:
        conn.execute("""
            INSERT INTO inspections
            (inspected_at, student_id, student_name, student_class,
             long_hair, colored_hair, color_note, ai_notes, reviewer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            student_id.strip(), student_name.strip(), student_class.strip(),
            long_hair, colored_hair, color_note.strip(),
            ai_notes.strip(), reviewer.strip()
        ))
        conn.commit()

def get_all():
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM inspections ORDER BY inspected_at DESC"
        ).fetchall()

def delete_inspection(record_id):
    with connect() as conn:
        conn.execute("DELETE FROM inspections WHERE id = ?", (record_id,))
        conn.commit()
