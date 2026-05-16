# Placeholder for risk_extractor.py service
import json
from datetime import datetime

from langchain_ollama import ChatOllama
from sqlalchemy import text

from backend.database import engine
from backend.services.vector_store import get_vector_store


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)


def load_risk_extraction_prompt() -> str:
    """
    Load the risk extraction prompt template.
    """

    with open("backend/prompts/risk_extraction_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


def clean_json_response(response_text: str) -> str:
    """
    Local LLMs sometimes wrap JSON inside markdown.
    This function tries to clean the response before json.loads().
    """

    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def extract_risks_from_documents() -> dict:
    """
    Retrieve relevant audit chunks from ChromaDB,
    ask Ollama to extract risks,
    save risks into SQLite,
    and return extracted risks.
    """

    vector_store = get_vector_store()

    search_queries = [
        "access control risk missing approval delayed access removal terminated user admin privilege",
        "vendor risk missing documentation annual review high risk vendor exception approval",
        "policy exception incomplete documentation compliance gap delayed review"
    ]

    all_docs = []

    for query in search_queries:
        docs = vector_store.similarity_search(query, k=6)
        all_docs.extend(docs)

    # Remove duplicate chunks by file name + chunk id
    unique_docs = {}
    for doc in all_docs:
        file_name = doc.metadata.get("file_name", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "unknown")
        unique_docs[(file_name, chunk_id)] = doc

    docs = list(unique_docs.values())

    if not docs:
        return {
            "risks": [],
            "message": "No document chunks found in ChromaDB. Upload documents first."
        }

    context_parts = []

    for doc in docs:
        file_name = doc.metadata.get("file_name", "unknown file")
        chunk_id = doc.metadata.get("chunk_id", "unknown chunk")

        context_parts.append(
            f"Source File: {file_name}\n"
            f"Chunk ID: {chunk_id}\n"
            f"Text:\n{doc.page_content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt_template = load_risk_extraction_prompt()

    final_prompt = prompt_template.replace("{context}", context)

    response = llm.invoke(final_prompt)
    content_str = str(response.content)

    cleaned_response = clean_json_response(content_str)

    try:
        risks = json.loads(cleaned_response)
    except json.JSONDecodeError:
        return {
            "error": "LLM did not return valid JSON.",
            "raw_response": content_str
        }

    if not isinstance(risks, list):
        return {
            "error": "LLM response was valid JSON but not a list.",
            "raw_response": risks
        }

    with engine.connect() as conn:
        for risk in risks:
            conn.execute(
                text("""
                    INSERT INTO risks
                    (
                        document_id,
                        risk_category,
                        severity,
                        evidence,
                        explanation,
                        confidence,
                        human_review_required,
                        created_at
                    )
                    VALUES
                    (
                        :document_id,
                        :risk_category,
                        :severity,
                        :evidence,
                        :explanation,
                        :confidence,
                        :human_review_required,
                        :created_at
                    )
                """),
                {
                    # Beginner simplification:
                    # Later we can map risks to exact document_id.
                    "document_id": 1,
                    "risk_category": risk.get("risk_category", "Unknown"),
                    "severity": risk.get("severity", "Medium"),
                    "evidence": risk.get("evidence", ""),
                    "explanation": risk.get("explanation", ""),
                    "confidence": risk.get("confidence", "Medium"),
                    "human_review_required": int(risk.get("human_review_required", True)),
                    "created_at": datetime.now().isoformat()
                }
            )

        conn.commit()

    return {
        "risks": risks,
        "risk_count": len(risks)
    }


def get_all_risks() -> list:
    """
    Read all extracted risks from SQLite.
    """

    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    risk_id,
                    risk_category,
                    severity,
                    evidence,
                    explanation,
                    confidence,
                    human_review_required,
                    created_at
                FROM risks
                ORDER BY risk_id DESC
            """)
        ).fetchall()

    risks = []

    for row in rows:
        risks.append(
            {
                "risk_id": row[0],
                "risk_category": row[1],
                "severity": row[2],
                "evidence": row[3],
                "explanation": row[4],
                "confidence": row[5],
                "human_review_required": bool(row[6]),
                "created_at": row[7]
            }
        )

    return risks