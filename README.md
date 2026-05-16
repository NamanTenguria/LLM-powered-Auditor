# AuditIQ

AuditIQ is a local, GenAI-powered audit risk review assistant. It helps internal audit teams upload evidence, ask questions, automatically extract risk signals, and generate structured audit findings—all while keeping data entirely on your local machine using local LLMs.

## 🚀 Core Features

1. **Upload Documents**: Support for TXT, CSV, PDF, and DOCX files. The backend extracts text, chunks it, creates embeddings, and stores it in ChromaDB.
2. **Ask AuditIQ**: Ask natural language questions about your audit documents. Powered by Retrieval-Augmented Generation (RAG).
3. **Risk Review**: Automatically scan the evidence vector store for common audit risks (like missing approvals or vendor issues) and save them to an SQLite database.
4. **Finding Generator**: Convert extracted risks into structured, ready-to-use audit findings for a non-technical audience.
5. **Dashboard**: View high-level metrics, risk severity breakdowns, and recently generated findings.
6. **Export Report**: Generate and download a comprehensive Markdown audit summary report.
7. **Admin Controls**: Safely wipe the SQLite database, Chroma vector store, and uploaded files for fresh demos.

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend API**: [FastAPI](https://fastapi.tiangolo.com/)
- **Local AI**: [Ollama](https://ollama.ai/) (running `llama3.2:3b` and `nomic-embed-text`)
- **LLM Orchestration**: [LangChain](https://python.langchain.com/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Relational Database**: SQLite & SQLAlchemy

## 📦 Setup & Installation

### 1. Install Prerequisites
You will need **Python 3.9+** and **Ollama** installed on your machine.
- [Download Ollama here](https://ollama.ai/download)

### 2. Pull Required Local Models
Before running the application, pull the necessary models via your terminal:
```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### 3. Setup the Python Environment
Clone this repository, navigate to the project folder, and set up a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

## 🏃‍♂️ Running the Application

To run AuditIQ, you need three separate terminal windows/tabs open in the project directory:

**Terminal 1: Start Ollama**
```bash
ollama serve
```
*(If the Ollama desktop app is already running in your menu bar, you can skip this step).*

**Terminal 2: Start the FastAPI Backend**
```bash
source venv/bin/activate
uvicorn backend.main:app --reload
```
*The API will be available at `http://localhost:8000` (Swagger UI at `/docs`).*

**Terminal 3: Start the Streamlit Frontend**
```bash
source venv/bin/activate
streamlit run frontend/streamlit_app.py
```
*The UI will open in your browser at `http://localhost:8501`.*

## 💡 Recommended Demo Workflow

If you want to test the end-to-end capabilities:
1. Navigate to the **Admin** tab and click **Reset Everything** for a clean slate.
2. Go to **Upload Documents** and upload your sample audit files.
3. Head to **Ask AuditIQ** and ask a question about the uploaded evidence.
4. Click **Run Risk Review** in the Risk Review tab to automatically extract risks.
5. Go to the **Finding Generator**, select one of the newly extracted risks, and generate a finding.
6. Check out your **Dashboard** metrics.
7. Go to **Export Report** and download your final markdown summary.

---
**Disclaimer**: *AuditIQ is designed to assist auditors, not replace professional judgment. All extracted risks and generated findings should be validated against source documents.*