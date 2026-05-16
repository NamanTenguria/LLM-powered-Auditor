# Placeholder for document_loader.py service

import os

import pandas as pd
from docx import Document
from pypdf import PdfReader


def load_text_from_file(file_path: str) -> str:
    """
    Extract text from TXT, CSV, PDF, and DOCX files.
    """

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".txt":
        return load_text_file(file_path)

    if file_extension == ".csv":
        return load_csv_file(file_path)

    if file_extension == ".pdf":
        return load_pdf_file(file_path)

    if file_extension == ".docx":
        return load_docx_file(file_path)

    raise ValueError(f"Unsupported file type: {file_extension}")


def load_text_file(file_path: str) -> str:
    """
    Read a plain text file.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def load_csv_file(file_path: str) -> str:
    """
    Read a CSV file and convert rows into text.
    """

    df = pd.read_csv(file_path)

    text_rows = []

    for row_idx, (index, row) in enumerate(df.iterrows()):
        row_text = ", ".join(
            [f"{column}: {row[column]}" for column in df.columns]
        )
        text_rows.append(f"Row {row_idx + 1}: {row_text}")

    return "\n".join(text_rows)


def load_pdf_file(file_path: str) -> str:
    """
    Extract text from a PDF file.
    """

    reader = PdfReader(file_path)
    text = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            text.append(f"Page {page_number}:\n{page_text}")

    return "\n\n".join(text)


def load_docx_file(file_path: str) -> str:
    """
    Extract text from a Word document.
    """

    doc = Document(file_path)

    paragraphs = [
        paragraph.text
        for paragraph in doc.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)