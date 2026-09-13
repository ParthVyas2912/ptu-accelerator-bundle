"""Create small, fictional Content Processing test inputs; never service outputs."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1] / "test-data" / "content"


def pdf(path, lines):
    """One-page PDF with ASCII text and a tabular estimate, no external data."""
    text = ["BT /F1 12 Tf 45 750 Td"]
    for i, line in enumerate(lines):
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if i:
            text.append("0 -22 Td")
        text.append(f"({escaped}) Tj")
    text.append("ET")
    stream = "\n".join(text).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream",
    ]
    content = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(content))
        content.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(content)
    content.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        content.extend(f"{offset:010} 00000 n \n".encode())
    content.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    path.write_bytes(content)


def main():
    vin = "1TST23456DEMO0001"
    common = ["FICTIONAL DEMONSTRATION - NOT A REAL CLAIM", "Claim: PTU-CONTENT-001", "Policy: TEST-POLICY-001"]
    form = common + [
        "AUTO INSURANCE CLAIM FORM", "Claimant: Alex Example",
        "Loss date: 2026-09-01", "Jurisdiction: TX", "Loss type: collision",
        "Vehicle VIN: " + vin, "Third party involved: Yes", "Injuries: No",
        "Incident: A fictional vehicle hit the left front bumper.",
        "Repair amount: USD 2500.00", "Police report number: TEST-PR-001",
    ]
    report = common + [
        "POLICE REPORT - FICTIONAL TRAINING RECORD", "Report number: TEST-PR-001",
        "Loss date: 2026-09-01", "Vehicle VIN: " + vin,
        "Incident: Collision with another fictional vehicle.", "Injuries: No",
    ]
    estimate = common + [
        "REPAIR ESTIMATE", "Vehicle VIN: " + vin, "Loss date: 2026-09-01",
        "Item                       Quantity    Unit USD      Total USD",
        "Front bumper                    1      1000.00        1000.00",
        "Labor                           5       200.00        1000.00",
        "Paint                           1       500.00         500.00",
        "TOTAL                                                 2500.00",
    ]
    for case in ["complete", "missing-police", "vin-date-mismatch", "visual-table", "corrupt"]:
        (ROOT / case).mkdir(parents=True, exist_ok=True)
    for case in ["complete", "missing-police", "vin-date-mismatch"]:
        folder = ROOT / case
        pdf(folder / "claim-form.pdf", form)
        pdf(folder / "repair-estimate.pdf", estimate)
        if case != "missing-police":
            selected = [s.replace(vin, "1TST23456DEMO0099").replace("2026-09-01", "2026-09-03") for s in report] if case == "vin-date-mismatch" else report
            pdf(folder / "police-report.pdf", selected)
    image = Image.new("RGB", (640, 360), "white")
    draw = ImageDraw.Draw(image)
    draw.text((20, 20), "FICTIONAL VEHICLE DIAGRAM - PTU-CONTENT-001", fill="black")
    draw.rectangle((130, 130, 490, 250), outline="black", width=5)
    draw.polygon([(210, 130), (260, 75), (380, 75), (440, 130)], outline="black", width=4)
    draw.ellipse((165, 220, 235, 290), fill="black")
    draw.ellipse((400, 220, 470, 290), fill="black")
    draw.line((130, 140, 165, 175, 130, 215), fill="red", width=8)
    draw.text((15, 310), "Red mark: simulated left front bumper damage; no injury shown.", fill="black")
    for case in ["complete", "missing-police", "vin-date-mismatch", "visual-table"]:
        image.save(ROOT / case / "damage-diagram.png")
    pdf(ROOT / "visual-table" / "repair-estimate.pdf", estimate)
    (ROOT / "corrupt" / "unsupported.txt").write_text("Synthetic unsupported text upload.", encoding="utf-8")
    (ROOT / "corrupt" / "bad-magic.pdf").write_bytes(b"NOT-A-PDF: fictional corrupt upload")
    (ROOT / "corrupt" / "truncated.pdf").write_bytes(b"%PDF-1.4\n1 0 obj\n<<\n")
    manifest = {
        "synthetic": True, "serviceOutputs": False, "claimId": "PTU-CONTENT-001",
        "vin": vin, "dateOfLoss": "2026-09-01", "repairTotalUSD": 2500,
        "expectedMissingRule": "REQ-PR-THIRD-PARTY-006",
        "expectedMismatchRules": ["DISC-VEHICLE-VIN-001", "DISC-DATE-OF-LOSS-001"],
        "note": "Inputs only. No claim processing success is implied. Image is a diagram, not a real photograph.",
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"generated_files": len(list(ROOT.rglob("*.*"))), "root": str(ROOT)}))


if __name__ == "__main__":
    main()
