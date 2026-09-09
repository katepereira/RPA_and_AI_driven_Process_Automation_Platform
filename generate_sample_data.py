"""
generate_sample_data.py
------------------------
Creates a few fake inspection certificate PDFs to test the pipeline with
— including one intentionally incomplete one, so you can demo the AI
validation actually catching something.

Run with: python generate_sample_data.py
Then drop files into incoming_certificates/ one at a time (or all at
once) to trigger watcher.py.
"""

from pathlib import Path
from reportlab.pdfgen import canvas

OUT_DIR = Path("incoming_certificates")
OUT_DIR.mkdir(exist_ok=True)

CERTIFICATES = [
    {
        "filename": "cert_001_clean.pdf",
        "lines": [
            "Seebot - INSPECTION CERTIFICATE",
            "Certificate No: TUV-2026-00458",
            "Inspection Date: 03/09/2026",
            "Inspector: Markus Weber",
            "Equipment: Pressure Vessel PV-114",
            "Result: PASS",
            "Notes: All safety parameters within tolerance.",
        ],
    },
    {
        "filename": "cert_002_conditional.pdf",
        "lines": [
            "Seebot - INSPECTION CERTIFICATE",
            "Certificate No: TUV-2026-00459",
            "Inspection Date: 04/09/2026",
            "Inspector: Anja Fischer",
            "Equipment: Elevator Unit EL-22",
            "Result: CONDITIONAL",
            "Notes: Minor wear on cable, re-inspect in 30 days.",
        ],
    },
    {
        "filename": "cert_003_incomplete.pdf",
        "lines": [
            "Seebot - INSPECTION CERTIFICATE",
            "Certificate No: TUV-2026-00460",
            "Equipment: Boiler B-9",
            "Result: FAIL",
            "Notes: Inspector field missing due to form error.",
        ],
    },
]


def make_pdf(filename: str, lines: list):
    path = OUT_DIR / filename
    c = canvas.Canvas(str(path))
    y = 800
    for line in lines:
        c.drawString(50, y, line)
        y -= 25
    c.save()
    print(f"Created {path}")


if __name__ == "__main__":
    for cert in CERTIFICATES:
        make_pdf(cert["filename"], cert["lines"])
