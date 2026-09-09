"""
claude_validator.py
--------------------
The "AI" half of the AI-driven automation platform. Regex extraction is
brittle and dumb; this module hands the raw text + extracted fields to
Claude and asks it to (a) sanity-check the extraction, (b) flag anything
inconsistent or missing, and (c) write a one-line human-readable summary.

Requires an ANTHROPIC_API_KEY environment variable. Get one at
https://console.anthropic.com/settings/keys
"""

import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

VALIDATION_PROMPT = """You are a QA assistant for an inspection/certification back-office.
You are given raw OCR/text extracted from a certificate PDF, plus fields a regex
extractor pulled out of it. Your job:

1. Decide if the extracted fields look complete and internally consistent.
2. List any specific issues (missing field, date looks malformed, result value
   not one of PASS/FAIL/CONDITIONAL, name looks truncated, etc).
3. Write a one-sentence plain-English summary of this certificate.

Respond ONLY with JSON, no other text, in exactly this shape:
{{"status": "ok" | "needs_review", "issues": ["..."], "summary": "..."}}

RAW TEXT:
{raw_text}

EXTRACTED FIELDS:
{fields_json}
"""


def validate_certificate(raw_text: str, fields: dict) -> dict:
    prompt = VALIDATION_PROMPT.format(
        raw_text=raw_text[:4000],  # keep prompt small; this is a demo, not a full doc pipeline
        fields_json=json.dumps(fields, indent=2),
    )

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "status": "needs_review",
            "issues": ["Claude response could not be parsed as JSON"],
            "summary": text[:200],
        }
