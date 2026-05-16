# Placeholder for risks.py router
from fastapi import APIRouter

from backend.services.risk_extractor import (
    extract_risks_from_documents,
    get_all_risks
)

router = APIRouter()


@router.post("/extract-risks")
def extract_risks():
    """
    Extract audit risks from documents stored in ChromaDB.
    """

    return extract_risks_from_documents()


@router.get("/risks")
def risks():
    """
    Return all extracted risks from SQLite.
    """

    return {
        "risks": get_all_risks()
    }