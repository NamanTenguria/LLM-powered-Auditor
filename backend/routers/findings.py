# Placeholder for findings.py router
from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.finding_generator import (
    generate_finding_from_risk,
    get_all_findings
)

router = APIRouter()


class FindingRequest(BaseModel):
    risk_id: int


@router.post("/generate-finding")
def generate_finding(request: FindingRequest):
    """
    Generate a structured audit finding from a selected risk.
    """

    return generate_finding_from_risk(request.risk_id)


@router.get("/findings")
def findings():
    """
    Return all generated findings from SQLite.
    """

    return {
        "findings": get_all_findings()
    }