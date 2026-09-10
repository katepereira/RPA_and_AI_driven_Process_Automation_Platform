# RPA and AI-Driven Process Automation Platform

Automates the intake of inspection/certification documents: extracts
structured data from PDFs, validates it with an LLM, logs a full audit
trail, and flags anything that needs human review — demonstrated through
two parallel automation paths (a Python RPA script and a no-code n8n
workflow) hitting the same backend.

Built as a demo of a certification-document intake pipeline (the kind of
repetitive, document-heavy process a testing/inspection/certification
company deals with daily), using synthetic sample data.

## What it does

1. A new certificate PDF appears in a watched folder.
2. It's picked up automatically — either by a Python script (`watcher.py`)
   or an n8n workflow — with no human involved.
3. Text and structured fields (certificate number, inspection date,
   inspector, result) are extracted from the PDF.
4. An AI validation step checks the extraction for completeness and
   consistency, and writes a short summary.
5. Every result is logged to a structured, timestamped JSON audit trail.
6. If something looks wrong (missing field, inconsistent value), the
   workflow branches and fires a review notification instead of silently
   filing it away.

## Architecture

```
incoming_certificates/  (new PDF appears)
        |
        +--> watcher.py (Python, RPA)  --\
        |                                 >--> FastAPI backend --> results_log.json
        +--> n8n workflow (no-code)    --/         |
                                                    +--> AI validation (Claude API)
                                                    |
                                                    +--> notification on flagged items
```

Two independent "front doors" — a hand-written Python automation script
and a no-code n8n workflow — both call the exact same backend endpoint.
This was deliberate: it demonstrates both custom RPA scripting and
operating a standard low-code automation tool against one shared service,
rather than building the same logic twice.

## Tech stack

- **Backend:** Python, FastAPI
- **RPA / automation:** `watchdog` (Python folder monitoring), n8n
  (no-code workflow orchestration)
- **AI validation:** Claude API (Anthropic)
- **Document parsing:** `pdfplumber`, regex-based field extraction
- **Data:** structured JSON audit log (no database dependency for this
  scale)

## Getting started

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-your-key-here

python generate_sample_data.py     # creates sample test certificates
uvicorn main:app --reload --port 8001
```

In a second terminal:
```bash
source venv/bin/activate
python watcher.py
```

Drop a PDF into `incoming_certificates/` and watch it get processed
automatically. Full setup notes, including the n8n workflow, live in
[`SETUP.md`](SETUP.md).

## Project structure

| File | Purpose |
|---|---|
| `main.py` | FastAPI backend — the core orchestration API |
| `watcher.py` | Python RPA: watches for new PDFs, calls the backend automatically |
| `extractor.py` | PDF text extraction + regex field parsing |
| `claude_validator.py` | AI validation layer (Claude API) |
| `results_log.py` | Structured JSON audit-trail logging |
| `n8n_workflow.json` | Importable no-code equivalent of `watcher.py` |
| `generate_sample_data.py` | Creates synthetic test certificates |

## Notes

- All sample certificates are synthetically generated for demo purposes —
  no real inspection data is used anywhere in this project.
- The AI validation step exists specifically to catch a class of error
  regex extraction alone can't: during testing, a naive regex matched
  the word "Inspector" from an unrelated notes field on an incomplete
  certificate, producing a plausible-looking but wrong value. The
  Claude validation step catches exactly this kind of extraction error
  regex can't self-check.

## License

MIT — feel free to fork and adapt.