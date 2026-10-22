"""
database.py
SQLite database management for Prakriti AI.
Provides schema definitions, connection management, and helper functions.
"""

import os
import sqlite3
from contextlib import contextmanager

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prakriti.db")

def get_db_path():
    return os.environ.get("PRAKRITI_DB_PATH", DEFAULT_DB_PATH)

@contextmanager
def get_db_connection(db_path=None):
    """Context manager for SQLite database connection with row factory and foreign keys."""
    path = db_path or get_db_path()
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(db_path=None):
    """Initializes tables for users, cycle logs, assessments, and wellness records."""
    with get_db_connection(db_path) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            age INTEGER,
            height_cm REAL,
            weight_kg REAL,
            bmi REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cycle_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            start_date TEXT NOT NULL,
            end_date TEXT,
            cycle_length INTEGER NOT NULL,
            menses_length INTEGER NOT NULL,
            pain_level INTEGER DEFAULT 0,
            flow_intensity TEXT DEFAULT 'Moderate',
            symptoms TEXT,
            predicted_regularity TEXT,
            regularity_confidence REAL,
            predicted_ovulation_day REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pcos_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            age INTEGER NOT NULL,
            cycle_length INTEGER NOT NULL,
            primary_concern TEXT NOT NULL,
            symptoms_list TEXT NOT NULL,
            pain_level INTEGER,
            flow_intensity TEXT,
            sleep_quality TEXT,
            screening_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            medical_assessment TEXT,
            ayurvedic_perspective TEXT,
            recommendations TEXT,
            disclaimer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS wellness_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            gender TEXT DEFAULT 'Female',
            sleep_duration REAL NOT NULL,
            quality_of_sleep INTEGER NOT NULL,
            activity_minutes INTEGER NOT NULL,
            stress_level INTEGER NOT NULL,
            bmi_category TEXT NOT NULL,
            heart_rate INTEGER,
            daily_steps INTEGER,
            systolic_bp INTEGER,
            diastolic_bp INTEGER,
            predicted_disorder TEXT,
            confidence REAL,
            probabilities_json TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS consultation_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            doctor_name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            preferred_date TEXT NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_cycle_user ON cycle_logs(user_id, start_date);
        CREATE INDEX IF NOT EXISTS idx_assessment_user ON pcos_assessments(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_wellness_user ON wellness_logs(user_id, created_at);
        """)
    return True

if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully at:", get_db_path())
