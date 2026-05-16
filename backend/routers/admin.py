import os
import shutil

from fastapi import APIRouter
from sqlalchemy import text

from backend.database import engine

router = APIRouter()


@router.post("/admin/reset-database")
def reset_database():
    """
    Delete app-generated records from SQLite.
    This keeps the tables but clears saved data.
    """

    with engine.connect() as conn:
        conn.execute(text("DELETE FROM qa_logs;"))
        conn.execute(text("DELETE FROM findings;"))
        conn.execute(text("DELETE FROM risks;"))
        conn.execute(text("DELETE FROM documents;"))
        conn.commit()

    return {
        "message": "SQLite database records cleared successfully."
    }


@router.post("/admin/reset-chroma")
def reset_chroma():
    """
    Delete local ChromaDB vector store files.
    """

    chroma_dir = "data/chroma_db"

    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir)

    os.makedirs(chroma_dir, exist_ok=True)

    return {
        "message": "ChromaDB vector store cleared successfully."
    }


@router.post("/admin/reset-uploads")
def reset_uploads():
    """
    Delete uploaded files from data/uploads.
    """

    upload_dir = "data/uploads"

    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)

    os.makedirs(upload_dir, exist_ok=True)

    return {
        "message": "Uploaded files cleared successfully."
    }


@router.post("/admin/reset-all")
def reset_all():
    """
    Clear SQLite records, ChromaDB data, and uploaded files.
    """

    with engine.connect() as conn:
        conn.execute(text("DELETE FROM qa_logs;"))
        conn.execute(text("DELETE FROM findings;"))
        conn.execute(text("DELETE FROM risks;"))
        conn.execute(text("DELETE FROM documents;"))
        conn.commit()

    chroma_dir = "data/chroma_db"
    upload_dir = "data/uploads"

    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir)

    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)

    os.makedirs(chroma_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)

    return {
        "message": "All app data cleared successfully."
    }