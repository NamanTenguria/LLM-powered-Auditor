# Placeholder for finding_generator.py service
import json
from datetime import datetime

from langchain_ollama import ChatOllama
from sqlalchemy import text

from backend.database import engine


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)


def load_finding_prompt() -> str:
    """
    Load the audit finding prompt template.
    """

    with open("backend/prompts/finding_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


def clean_json_response(response_text: str) -> str:
    """
    Local LLMs sometimes wrap JSON inside markdown.
    This cleans common formatting issues.
    """

    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def get_risk_by_id(risk_id: int):
    """
    Load one risk from SQLite using risk_id.
    """

    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT
                    risk_id,
                    risk_category,
                    severity,
                    evidence,
                    explanation,
                    confidence,
                    human_review_required
                FROM risks
                WHERE risk_id = :risk_id
            """),
            {"risk_id": risk_id}
        ).fetchone()

    if row is None:
        return None

    return {
        "risk_id": row[0],
        "risk_category": row[1],
        "severity": row[2],
        "evidence": row[3],
        "explanation": row[4],
        "confidence": row[5],
        "human_review_required": bool(row[6])
    }


def generate_finding_from_risk(risk_id: int) -> dict:
    """
    Generate a structured audit finding from one selected risk.
    """

    risk = get_risk_by_id(risk_id)

    if risk is None:
        return {
            "error": "Risk not found. Run Risk Review first or choose a valid risk_id."
        }

    prompt_template = load_finding_prompt()

    final_prompt = prompt_template.replace(
        "{risk}", json.dumps(risk, indent=2)
    )

    response = llm.invoke(final_prompt)
    content_str = str(response.content)

    cleaned_response = clean_json_response(content_str)

    try:
        finding = json.loads(cleaned_response)
    except json.JSONDecodeError:
        return {
            "error": "LLM did not return valid JSON.",
            "raw_response": content_str
        }

    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO findings
                (
                    risk_id,
                    title,
                    condition,
                    criteria_text,
                    cause,
                    impact,
                    recommendation,
                    severity,
                    created_at
                )
                VALUES
                (
                    :risk_id,
                    :title,
                    :condition,
                    :criteria_text,
                    :cause,
                    :impact,
                    :recommendation,
                    :severity,
                    :created_at
                )
            """),
            {
                "risk_id": risk_id,
                "title": finding.get("title", ""),
                "condition": finding.get("condition", ""),
                "criteria_text": finding.get("criteria_text", ""),
                "cause": finding.get("cause", ""),
                "impact": finding.get("impact", ""),
                "recommendation": finding.get("recommendation", ""),
                "severity": finding.get("severity", risk.get("severity", "Medium")),
                "created_at": datetime.now().isoformat()
            }
        )

        conn.commit()

    return finding


def get_all_findings() -> list:
    """
    Load all generated findings from SQLite.
    """

    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    finding_id,
                    risk_id,
                    title,
                    condition,
                    criteria_text,
                    cause,
                    impact,
                    recommendation,
                    severity,
                    created_at
                FROM findings
                ORDER BY finding_id DESC
            """)
        ).fetchall()

    findings = []

    for row in rows:
        findings.append(
            {
                "finding_id": row[0],
                "risk_id": row[1],
                "title": row[2],
                "condition": row[3],
                "criteria_text": row[4],
                "cause": row[5],
                "impact": row[6],
                "recommendation": row[7],
                "severity": row[8],
                "created_at": row[9]
            }
        )

    return findings