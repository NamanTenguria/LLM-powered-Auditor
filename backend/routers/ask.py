# Placeholder for ask.py router
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from backend.database import engine
from backend.services.rag_chain import answer_question

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(request: AskRequest):
    """
    Receive a question from the frontend,
    answer it using RAG,
    save the Q&A log to SQLite,
    and return the answer plus sources.
    """

    result = answer_question(request.question)

    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO qa_logs 
                (question, answer, sources, created_at)
                VALUES (:question, :answer, :sources, :created_at)
            """),
            {
                "question": request.question,
                "answer": result["answer"],
                "sources": str(result["sources"]),
                "created_at": datetime.now().isoformat()
            }
        )

        conn.commit()

    return result