# Placeholder for database.py
from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///database/auditiq.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


def init_db():
    """
    Create all required SQLite tables if they do not already exist.
    """

    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                document_type TEXT,
                upload_time TEXT,
                chunk_count INTEGER,
                status TEXT
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS risks (
                risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                risk_category TEXT,
                severity TEXT,
                evidence TEXT,
                explanation TEXT,
                confidence TEXT,
                human_review_required INTEGER,
                created_at TEXT
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS findings (
                finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
                risk_id INTEGER,
                title TEXT,
                condition TEXT,
                criteria_text TEXT,
                cause TEXT,
                impact TEXT,
                recommendation TEXT,
                severity TEXT,
                created_at TEXT
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS qa_logs (
                qa_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                sources TEXT,
                created_at TEXT
            );
        """))

        conn.commit()