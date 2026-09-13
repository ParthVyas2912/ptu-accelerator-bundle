"""Generate a single fictional table-PDF rendition of logical fixture 02, offline."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
path = root / "test-data/documents/02-policy-2026-table.pdf"
if path.exists():
    raise SystemExit("Refusing to overwrite an existing evaluation fixture")
lines = [
    "SYNTHETIC / FICTIONAL / UNCLASSIFIED",
    "Person: Omar Patel; Place: Cedar Bay",
    "Document type: Policy; Version: 2026; active",
    "Supersedes the 2025 training policy.",
]
commands = ["BT /F1 11 Tf 36 744 Td 22 TL"]
for i, line in enumerate(lines):
    if i:
        commands.append("T*")
    commands.append(f"({line}) Tj")
commands += ["ET", "36 600 420 52 re S", "36 626 m 456 626 l S", "316 600 m 316 652 l S",
             "BT /F1 11 Tf 44 635 Td (Allowance) Tj 280 0 Td (Days/year) Tj ET",
             "BT /F1 11 Tf 44 609 Td (Annual training) Tj 280 0 Td (15) Tj ET"]
stream = "\n".join(commands).encode("ascii")
objects = [
    b"<< /Type /Catalog /Pages 2 0 R >>",
    b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
    b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
    b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
    f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream",
]
content = bytearray(b"%PDF-1.4\n")
offsets = [0]
for number, obj in enumerate(objects, 1):
    offsets.append(len(content))
    content += f"{number} 0 obj\n".encode() + obj + b"\nendobj\n"
xref = len(content)
content += f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode()
for offset in offsets[1:]:
    content += f"{offset:010d} 00000 n \n".encode()
content += f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
path.write_bytes(content)
result = {
    "logical_fixture": "02-policy-2026", "uploaded": False,
    "original_rendition": "02-policy-2026.txt", "evaluation_rendition": path.name,
    "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "pages": 1,
    "expected_metadata": {"person": "Omar Patel", "place": "Cedar Bay", "document_type": "Policy"},
    "expected_facts": {"year": 2026, "status": "active", "training_days": 15},
    "extraction": "Original PdfMarkdownDecoder using Document Intelligence prebuilt-layout",
    "coverage": "Alternative rendition of logical case02; not an eleventh logical test or a ten-document pass.",
}
(root / "evidence/documents/second-policy-fixture.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
