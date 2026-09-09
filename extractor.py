"""
extractor.py
------------
Pulls raw text out of an inspection/certificate PDF and parses a handful
of structured fields out of it with regex. This is the "RPA" data-entry
replacement step: turning an unstructured PDF into structured JSON
without a human retyping it.
"""

import re
import pdfplumber


FIELD_PATTERNS = {
    "certificate_number": r"Certificate\s*(?:No\.?|Number)\s*:?\s*([A-Z0-9\-\/]+)",
    "inspection_date": r"Inspection\s*Date\s*:?\s*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4})",
    "inspector_name": r"Inspector\s*:?\s*([A-Za-z\.\s]+?)(?:\n|$)",
    "result": r"Result\s*:?\s*(PASS|FAIL|CONDITIONAL)",
    "equipment": r"Equipment\s*:?\s*([A-Za-z0-9\-\s]+?)(?:\n|$)",
}

REQUIRED_FIELDS = ["certificate_number", "inspection_date", "inspector_name", "result"]


def extract_text(pdf_path: str) -> str:
    text_chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)


def extract_fields(raw_text: str) -> dict:
    fields = {}
    for field_name, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, raw_text, re.IGNORECASE)
        fields[field_name] = match.group(1).strip() if match else None
    return fields


def missing_required_fields(fields: dict) -> list:
    return [f for f in REQUIRED_FIELDS if not fields.get(f)]
