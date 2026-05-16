# Placeholder for upload.py router
import os
import shutil
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form
from sqlalchemy import text

from backend.database import engine
from backend.services.document_loader import load_text_from_file
from backend.services.vector_store import split_text_into_chunks, add_documents_to_chroma

router = APIRouter()

UPLOAD_DIR = "data/uploads"


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...)
):
    """
    Upload a document, extract text, split it into chunks,
    store embeddings in ChromaDB, and save metadata in SQLite.
    """

    filename = file.filename or "unknown_document"

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = load_text_from_file(file_path)

    documents = split_text_into_chunks(
        text=extracted_text,
        file_name=filename
    )

    chunk_count = add_documents_to_chroma(documents)

    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO documents
                (file_name, document_type, upload_time, chunk_count, status)
                VALUES (:file_name, :document_type, :upload_time, :chunk_count, :status)
            """),
            {
                "file_name": filename,
                "document_type": document_type,
                "upload_time": datetime.now().isoformat(),
                "chunk_count": chunk_count,
                "status": "processed"
            }
        )

        conn.commit()

    return {
        "message": "Document uploaded and processed successfully.",
        "file_name": filename,
        "document_type": document_type,
        "chunk_count": chunk_count,
        "status": "processed"
    }