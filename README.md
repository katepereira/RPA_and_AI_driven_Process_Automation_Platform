# RPA and AI-Driven Process Automation Platform

Automates intake of inspection/certificate PDFs: extracts structured data,
validates it with Claude, logs everything, and flags anything that needs
human review. Built to demo both a pure-Python RPA path and a no-code
(n8n) path against the same backend.

## Architecture

```
incoming_certificates/  (new PDF appears)
        |
        +--> watcher.py (Python, RPA)  --\
        |                                 >--> FastAPI backend --> results_log.json
        +--> n8n workflow (no-code)    --/         |
                                                    +--> Claude API (validation)
                                                    |
                                                    +--> notification (email/Slack)
```

Two different "front doors" (a Python script, and a no-code n8n flow) both
call the *same* FastAPI service. That's deliberate — it lets you demo the
RPA-scripting side and the low-code-automation-tool side without
duplicating any of the actual logic.

## Part 1 — VS Code / Python side

1. Open the `rpa-ai-platform` folder in VS Code.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Get an Anthropic API key from https://console.anthropic.com/settings/keys
   and set it as an environment variable:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...     # Windows: set ANTHROPIC_API_KEY=sk-ant-...
   ```
4. Generate sample test certificates:
   ```bash
   python generate_sample_data.py
   ```
   This drops 3 fake PDFs into `incoming_certificates/` (one clean, one
   conditional, one deliberately incomplete — good for showing off the
   AI validation catching a problem).
5. Start the backend:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Visit `http://localhost:8000/docs` — FastAPI's auto-generated Swagger
   UI, useful for testing `/process-certificate` by hand before wiring up
   automation on top of it.
6. In a second terminal, start the watcher:
   ```bash
   python watcher.py
   ```
   Now `incoming_certificates/` is being watched live. Copy a new PDF in
   (or re-run `generate_sample_data.py` with a new filename) and watch it
   get picked up, processed, and moved to `processed/` automatically.
7. Check results any time:
   ```bash
   curl http://localhost:8000/logs
   ```
   or open `processed/results_log.json` directly.

At this point you have a fully working RPA + AI pipeline in pure Python —
no other tool required. This alone satisfies "script-based tools to
digitize operational routines."

## Part 2 — n8n (the no-code RPA/automation layer)

n8n is a separate application — it is **not** a VS Code extension or a
Python package. It's a workflow-automation server you run alongside your
Python project, and the two talk to each other purely over HTTP (your
FastAPI app is just an API from n8n's point of view — no special
integration needed).

1. Install and run n8n (no Docker needed — just Node.js):
   ```bash
   npx n8n
   ```
   This opens the n8n editor at `http://localhost:5678` in your browser.
   (First run asks you to create a local owner account — that's normal,
   it's just protecting your local instance.)
2. In the n8n editor: **Workflows -> Import from File** and select
   `n8n_workflow.json` from this project. This gives you a starting
   point with 4 nodes already wired together:
   - **Schedule Trigger** - polls on an interval (open the node and set
     it to every 30-60 seconds)
   - **Read/Write Files** - reads new PDFs from `incoming_certificates/`
     (update the file path to the absolute path on your machine)
   - **HTTP Request** - POSTs the PDF to your FastAPI backend at
     `http://localhost:8000/process-certificate` (this is the exact
     same endpoint `watcher.py` calls — same backend, different trigger)
   - **IF** node - branches on whether Claude flagged the certificate as
     `needs_review`, sending an email (or Slack — swap the node) only
     when something actually needs a human
3. Make sure `uvicorn` is still running (from Part 1) — n8n calls into
   it exactly like `watcher.py` does.
4. Click **Execute Workflow** in the n8n editor to test it manually, or
   turn the workflow **Active** to let the schedule trigger run it for
   real.

That's "connecting n8n to VS Code": there's no plugin or bridge — n8n and
your FastAPI app are two independent local servers, and n8n's HTTP
Request node is simply calling `localhost:8000` the same way a browser
or curl would. Keep both terminals (`uvicorn` and `npx n8n`) running side
by side while you develop.

## Mapping this back to your CV bullets

- **"Designed and built automated process workflows and script-based
  tools to digitize operational routines"** -> `watcher.py` (zero-touch
  folder automation) + `extractor.py` (turns unstructured PDF text into
  structured fields without manual data entry).
- **"Evaluated and integrated automation frameworks and AI solutions to
  optimize repetitive data processing tasks"** -> the n8n workflow
  (evaluating a no-code RPA framework) alongside Claude API validation
  (the AI solution layer catching extraction errors regex alone misses
  — you actually saw this happen with the "Inspector" mis-capture during
  testing, which is a great concrete example to bring up).

## Talking points for the interview

- Why two front doors (Python script + n8n) instead of one: shows you
  can both write custom automation code *and* operate a standard no-code
  RPA tool — which is exactly the dual skill set an "IT, RPA und KI"
  Werkstudent role is testing for.
- Why validation is a separate AI step rather than smarter regex: regex
  extraction is fast and free but brittle (demonstrated by the
  `cert_003_incomplete.pdf` test case); an LLM catches semantic problems
  regex structurally cannot (missing fields, inconsistent values,
  malformed dates) — a realistic argument for *when* to reach for AI vs.
  when simpler tooling is enough, which is a good instinct to
  articulate out loud.
- The `results_log.json` audit trail mirrors the `ResultsLog`/`Timer`
  pattern you already built for your AutoML course project — it's the
  same instinct (structured, inspectable logging over ad-hoc prints)
  applied to a different domain, worth mentioning if asked about your
  approach to engineering discipline.

## Honesty notes (per your own standard)

Everything in this project is genuinely yours to claim if you build and
run it as described: real Python, real FastAPI, real n8n workflow, real
Claude API calls. If asked in the interview, you can honestly say you
built a demo with realistic (synthetic) inspection certificates rather
than real TÜV data — that's an accurate and unremarkable thing to say
about any portfolio project.
