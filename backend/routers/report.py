from fastapi import APIRouter

from backend.services.report_generator import generate_markdown_report

router = APIRouter()


@router.get("/export-report")
def export_report():
    """
    Generate and return a Markdown audit summary report.
    """

    return generate_markdown_report()