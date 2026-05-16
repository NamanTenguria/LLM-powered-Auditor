# Placeholder for dashboard.py router
from fastapi import APIRouter
from sqlalchemy import text

from backend.database import engine

router = APIRouter()


@router.get("/dashboard")
def dashboard():
    """
    Return summary metrics for the AuditIQ dashboard.
    """

    with engine.connect() as conn:
        documents_reviewed = conn.execute(
            text("SELECT COUNT(*) FROM documents")
        ).scalar()

        risks_detected = conn.execute(
            text("SELECT COUNT(*) FROM risks")
        ).scalar()

        findings_generated = conn.execute(
            text("SELECT COUNT(*) FROM findings")
        ).scalar()

        high_severity_risks = conn.execute(
            text("SELECT COUNT(*) FROM risks WHERE severity = 'High'")
        ).scalar()

        medium_severity_risks = conn.execute(
            text("SELECT COUNT(*) FROM risks WHERE severity = 'Medium'")
        ).scalar()

        low_severity_risks = conn.execute(
            text("SELECT COUNT(*) FROM risks WHERE severity = 'Low'")
        ).scalar()

        human_review_required = conn.execute(
            text("SELECT COUNT(*) FROM risks WHERE human_review_required = 1")
        ).scalar()

        risks_by_category_rows = conn.execute(
            text("""
                SELECT risk_category, COUNT(*) AS count
                FROM risks
                GROUP BY risk_category
                ORDER BY count DESC
            """)
        ).fetchall()

        risks_by_severity_rows = conn.execute(
            text("""
                SELECT severity, COUNT(*) AS count
                FROM risks
                GROUP BY severity
                ORDER BY count DESC
            """)
        ).fetchall()

        recent_risks_rows = conn.execute(
            text("""
                SELECT risk_id, risk_category, severity, evidence, confidence, created_at
                FROM risks
                ORDER BY risk_id DESC
                LIMIT 10
            """)
        ).fetchall()

        recent_findings_rows = conn.execute(
            text("""
                SELECT finding_id, risk_id, title, severity, created_at
                FROM findings
                ORDER BY finding_id DESC
                LIMIT 10
            """)
        ).fetchall()

    return {
        "documents_reviewed": documents_reviewed,
        "risks_detected": risks_detected,
        "findings_generated": findings_generated,
        "high_severity_risks": high_severity_risks,
        "medium_severity_risks": medium_severity_risks,
        "low_severity_risks": low_severity_risks,
        "human_review_required": human_review_required,
        "risks_by_category": [
            {"risk_category": row[0], "count": row[1]}
            for row in risks_by_category_rows
        ],
        "risks_by_severity": [
            {"severity": row[0], "count": row[1]}
            for row in risks_by_severity_rows
        ],
        "recent_risks": [
            {
                "risk_id": row[0],
                "risk_category": row[1],
                "severity": row[2],
                "evidence": row[3],
                "confidence": row[4],
                "created_at": row[5]
            }
            for row in recent_risks_rows
        ],
        "recent_findings": [
            {
                "finding_id": row[0],
                "risk_id": row[1],
                "title": row[2],
                "severity": row[3],
                "created_at": row[4]
            }
            for row in recent_findings_rows
        ]
    }