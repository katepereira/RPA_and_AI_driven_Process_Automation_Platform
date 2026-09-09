"""
main.py
-------
FastAPI backend for the RPA + AI-Driven Process Automation Platform.

This is the "brain": it receives a certificate PDF (from the Python
watcher script OR from n8n), extracts structured fields, runs them past
Claude for validation, logs the result, and returns JSON that n8n (or
anything else) can branch on.

Run with:  uvicorn main:app --reload --port 8000
Docs at:   http://localhost:8000/docs
"""

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from extractor import extract_text, extract_fields, missing_required_fields
from claude_validator import validate_certificate
from results_log import ResultsLog, Timer

app = FastAPI(title="RPA + AI Process Automation Platform")
log = ResultsLog()


class ProcessResult(BaseModel):
    id: int
    filename: str
    fields: dict
    missing_fields: list
    ai_status: str
    ai_issues: list
    ai_summary: str
    processing_seconds: float


@app.get("/")
def root():
    return {"service": "rpa-ai-platform", "status": "running", "docs": "/docs"}


@app.post("/process-certificate", response_model=ProcessResult)
async def process_certificate(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    with Timer() as t:
        # Save upload to a temp path so pdfplumber can read it
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            raw_text = extract_text(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        fields = extract_fields(raw_text)
        missing = missing_required_fields(fields)

        ai_result = validate_certificate(raw_text, fields)

    record = log.add({
        "filename": file.filename,
        "fields": fields,
        "missing_fields": missing,
        "ai_status": ai_result.get("status", "needs_review"),
        "ai_issues": ai_result.get("issues", []),
        "ai_summary": ai_result.get("summary", ""),
        "processing_seconds": t.elapsed_seconds,
    })

    return record


@app.get("/logs")
def get_logs():
    return log.all()


@app.get("/logs/{record_id}")
def get_log(record_id: int):
    record = log.get(record_id)
    if not record:
        raise HTTPException(404, "Record not found")
    return record
