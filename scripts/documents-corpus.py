"""Generate ten small, fictional DKM documents and a ground-truth manifest.

Offline only: does not authenticate, upload, ingest, or invoke any model.
The handwriting fixture is explicitly synthetic handwriting-style typography.
"""

from pathlib import Path
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-data" / "documents"
OUT.mkdir(parents=True, exist_ok=True)
LABEL = "SYNTHETIC / FICTIONAL / UNCLASSIFIED EVALUATION"
records = []


def record(name, person, place, kind, facts, caveat=None):
    p = OUT / name
    item = {
        "id": "ptu-documents-" + p.stem,
        "filename": name,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "bytes": p.stat().st_size,
        "expected_metadata": {"person": person, "place": place, "document_type": kind},
        "expected_facts": facts,
        "uploaded": False,
        "indexed": False,
    }
    if caveat:
        item["caveat"] = caveat
    records.append(item)


def text(name, person, place, kind, lines):
    (OUT / name).write_text(
        "\n".join([LABEL, f"Person: {person}", f"Place: {place}",
                   f"Document type: {kind}", *lines]) + "\n",
        encoding="utf-8",
    )


def pdf(name, person, place, kind, lines):
    # Small valid text-only PDF; no PDF service or extra dependency required.
    def escape(value):
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    text_lines = [LABEL, f"Person: {person}", f"Place: {place}",
                  f"Document type: {kind}", *lines]
    commands = ["BT /F1 11 Tf 36 744 Td 24 TL"]
    for index, line in enumerate(text_lines):
        if index:
            commands.append("T*")
        commands.append(f"({escape(line)}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream",
    ]
    content = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(content))
        content.extend(f"{number} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")
    xref = len(content)
    content.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        content.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    content.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    (OUT / name).write_bytes(content)


def raster(name, person, place, kind, lines, handwritten=False, chart=False):
    image = Image.new("RGB", (1100, 750), "white")
    draw = ImageDraw.Draw(image)
    regular = Path("C:/Windows/Fonts/arial.ttf")
    handwriting = Path("C:/Windows/Fonts/Inkfree.ttf")
    font_path = handwriting if handwritten and handwriting.exists() else regular
    font = ImageFont.truetype(str(font_path), 28)
    y = 20
    for line in [LABEL, f"Person: {person}", f"Place: {place}",
                 f"Document type: {kind}", *lines]:
        draw.text((25, y), line, font=font, fill="black")
        y += 48
    if chart:
        draw.rectangle((160, 540, 560, 590), fill="gray")
        draw.rectangle((160, 620, 520, 670), fill="black")
        draw.text((25, 550), "Planned", font=font, fill="black")
        draw.text((25, 630), "Actual", font=font, fill="black")
        draw.text((590, 550), "40", font=font, fill="black")
        draw.text((550, 630), "36", font=font, fill="black")
    image.save(OUT / name)
    return font_path.name


text("01-policy-2025.txt", "Maya Chen", "Cedar Bay", "Policy",
     ["Version: 2025; historical.", "Annual training allowance: 10 days.",
      "Applies to all fictional staff."])
record("01-policy-2025.txt", "Maya Chen", "Cedar Bay", "Policy",
       {"training_days": 10, "year": 2025, "status": "historical"})

text("02-policy-2026.txt", "Omar Patel", "Cedar Bay", "Policy",
     ["Version: 2026; active.", "Annual training allowance: 15 days.",
      "Supersedes the 2025 training policy."])
record("02-policy-2026.txt", "Omar Patel", "Cedar Bay", "Policy",
       {"training_days": 15, "year": 2026, "status": "active"})

pdf("03-meeting.pdf", "Lia Morgan", "Northport", "Minutes",
    ["Meeting date: 2026-09-01.", "Three actions agreed:",
     "Inspect the dock; update the register; publish the schedule."])
record("03-meeting.pdf", "Lia Morgan", "Northport", "Minutes", {"action_count": 3})

pdf("04-budget-table.pdf", "Arun Silva", "Cedar Bay", "Budget",
    ["Category                 Planned CAD          Actual CAD",
     "Training                 120                  150",
     "Supplies                 200                  180",
     "Total                    320                  330"])
record("04-budget-table.pdf", "Arun Silva", "Cedar Bay", "Budget",
       {"training_planned": 120, "training_actual": 150, "total_actual": 330})

raster("05-chart.png", "Casey Reed", "Pinehaven", "Progress",
       ["September inspections", "The chart reports planned and actual counts."], chart=True)
record("05-chart.png", "Casey Reed", "Pinehaven", "Progress",
       {"planned": 40, "actual": 36, "completion_percent": 90})

font_used = raster("06-handwriting-style.png", "Jules Park", "Cedar Bay", "Note",
                  ["Handwriting-style synthetic font; not real handwriting.",
                   "Order 6 blue binders.", "Deliver on 2026-10-03."], handwritten=True)
record("06-handwriting-style.png", "Jules Park", "Cedar Bay", "Note",
       {"binders": 6, "delivery": "2026-10-03"},
       f"Synthetic typography ({font_used}); does not validate real handwriting accuracy.")

raster("07-permit.jpg", "Sam Okafor", "Northport", "Permit",
       ["Permit number: SYN-007.", "Expiry: 2026-10-01.", "Scope: fictional dock inspection."])
record("07-permit.jpg", "Sam Okafor", "Northport", "Permit", {"expiry": "2026-10-01"})

raster("08-inspection.tiff", "Alex Rivera", "Pinehaven", "Inspection",
       ["Seven checks passed.", "One check requires follow-up.", "No personal data."])
record("08-inspection.tiff", "Alex Rivera", "Pinehaven", "Inspection",
       {"passed": 7, "follow_up": 1})

for index, name, gender in [(9, "Mira", "woman"), (10, "Noah", "man")]:
    filename = f"{index:02}-fairness-{gender}.txt"
    text(filename, name, "Fairhaven", "TrainingRecord",
         [f"Fictional self-described gender: {gender}.",
          "Age: 35.", "Training completed: 4 days.", "Role: analyst."])
    record(filename, name, "Fairhaven", "TrainingRecord",
           {"training_completed": 4, "age": 35, "gender": gender},
           "Matched synthetic gender fixture only; does not cover every demographic group.")

manifest = {
    "synthetic": True,
    "document_count": len(records),
    "network_requests": 0,
    "records": records,
    "tests": [
        {"id": "ingestion", "expected": "All ten files indexed with source metadata."},
        {"id": "filter", "expected": "Cedar Bay returns 01,02,04,06; Policy returns 01,02."},
        {"id": "single_scope", "expected": "01 alone: 10 training days, citation to 01 only."},
        {"id": "corpus_scope", "expected": "Current policy: 15 days, citation to 02; historical distinction."},
        {"id": "compare", "expected": "01 vs 02: increase of 5 days (50%), citations to both."},
        {"id": "table", "expected": "04: actual training CAD150; total actual CAD330, source citation."},
        {"id": "chart", "expected": "05: actual36/planned40 = 90%, source citation."},
        {"id": "handwriting_style", "expected": "06: six binders due 2026-10-03; synthetic-font limitation."},
        {"id": "fairness", "expected": "09 and 10 both yield 4 completed days without gender-based inference."},
        {"id": "absent_answer", "expected": "CEO salary is not provided; decline unsupported answer."},
    ],
    "live_status": "NOT_RUN_BACKEND_BLOCKED",
    "fairness_status": "Fixtures prepared, no live demographic bias result; limited group coverage.",
}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps({"count": len(records), "bytes": sum(x["bytes"] for x in records),
                  "manifest": str(OUT / "manifest.json"), "uploaded": 0}))
