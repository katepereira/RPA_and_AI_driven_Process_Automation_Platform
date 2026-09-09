"""
claude_validator.py  (MOCK MODE - no API calls, no cost)
-----------------------------------------------------------
This is a drop-in stand-in for the real Claude-powered validator.
Same function name, same input, same output shape (status/issues/summary)
as the real one - so main.py and watcher.py need ZERO changes.

It runs simple rule-based checks instead of calling Claude, so you can
build, test, and demo the rest of the pipeline (extraction, watcher,
logging, n8n) completely free, with no API credit needed.

When your Anthropic billing/credits are sorted:
  1. Delete this file's contents (or rename it out of the way).
  2. Rename claude_validator_real.py -> claude_validator.py.
That's the only change needed to switch back to real AI validation.
"""

import time
import random

REQUIRED_FIELDS = ["certificate_number", "inspection_date", "inspector_name", "result"]
VALID_RESULTS = {"PASS", "FAIL", "CONDITIONAL"}


def validate_certificate(raw_text: str, fields: dict) -> dict:
    # Small artificial delay so this behaves like a real network call
    # in demos (instant responses look suspicious in a live walkthrough).
    time.sleep(random.uniform(0.3, 0.8))

    issues = []

    for field in REQUIRED_FIELDS:
        if not fields.get(field):
            issues.append(f"Missing required field: {field}")

    result_value = fields.get("result")
    if result_value and result_value.upper() not in VALID_RESULTS:
        issues.append(f"Unexpected result value: '{result_value}' (expected PASS/FAIL/CONDITIONAL)")

    inspector = fields.get("inspector_name") or ""
    if inspector and len(inspector.split()) > 6:
        issues.append("Inspector name looks abnormally long - possible extraction error")

    status = "needs_review" if issues else "ok"

    cert_num = fields.get("certificate_number", "unknown certificate")
    result_str = fields.get("result", "no result recorded")
    summary = f"[MOCK] Certificate {cert_num}: result={result_str}, {len(issues)} issue(s) flagged."

    return {
        "status": status,
        "issues": issues,
        "summary": summary,
    }