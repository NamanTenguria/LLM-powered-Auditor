from fastapi import FastAPI

from backend.database import init_db
from backend.routers import ask, upload, risks, findings, dashboard, report, admin

app = FastAPI(
    title="AuditIQ API",
    description="GenAI-powered audit risk review assistant",
    version="0.1.0"
)


@app.on_event("startup")
def startup_event():
    init_db()


app.include_router(upload.router)
app.include_router(ask.router)
app.include_router(risks.router)
app.include_router(findings.router)
app.include_router(dashboard.router)
app.include_router(report.router)
app.include_router(admin.router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AuditIQ backend is running"
    }