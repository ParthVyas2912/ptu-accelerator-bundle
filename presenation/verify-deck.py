"""Check the local deck package, notes and render coverage without Office uploads."""

from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
DECK = ROOT / "PTU-Accelerator-Internal-2026-09-14.pptx"
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
QA = ROOT / "qa"
QA.mkdir(exist_ok=True)
layout_warnings = json.loads((QA / "powerpoint-layout.json").read_text(encoding="utf-8-sig"))
assert layout_warnings == [], f"Resolve native PowerPoint layout warnings: {layout_warnings}"
extracted = []
with zipfile.ZipFile(DECK) as archive:
    slides = sorted(
        (name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
        key=lambda name: int(re.search(r"slide(\d+)\.xml", name).group(1)),
    )
    assert len(slides) == 16, f"Expected 16 slides, found {len(slides)}"
    for index, name in enumerate(slides, 1):
        xml = ET.fromstring(archive.read(name))
        text = "\n".join(node.text or "" for node in xml.findall(".//a:t", NS))
        assert len(text) > 100, f"Slide {index} is empty or incomplete"
        assert not re.search(r"lorem ipsum|click to (?:add|edit)|xxxx", text, re.I), index
        note_name = f"ppt/notesSlides/notesSlide{index}.xml"
        note_xml = ET.fromstring(archive.read(note_name))
        note_text = "\n".join(node.text or "" for node in note_xml.findall(".//a:t", NS))
        assert "Transition:" in note_text and "Suggested time:" in note_text, index
        assert len(note_text) > 500, f"Slide {index} has insufficient notes"
        assert (ROOT / "preview" / f"slide-{index:02}.png").is_file(), index
        extracted.append(f"SLIDE {index}\n{text}\n\nNOTES\n{note_text}\n")

full_text = "\n".join(extracted)
assert not re.search(r"\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", full_text, re.I)
assert not re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", full_text, re.I)
for required in [
    "No PTUs or reservations purchased",
    "Standard / Batch",
    "not yet implemented",
    "human",
    "processing geography",
    "NOT A COMMERCIAL SKU",
]:
    assert required.casefold() in full_text.casefold(), required
(QA / "extracted-deck.txt").write_text(full_text, encoding="utf-8")
assert (ROOT / "PTU-Accelerator-Internal-2026-09-14.pdf").stat().st_size > 10000
talking = (ROOT / "Talking-Points-2026-09-14.md").read_text(encoding="utf-8")
assert len(re.findall(r"^### \d+\.", talking, re.M)) == 16
assert "60-second opening" in talking and "Likely questions" in talking

for start in range(1, 17, 4):
    sheet = Image.new("RGB", (1600, 952), "#e0e0e0")
    draw = ImageDraw.Draw(sheet)
    for offset in range(4):
        number = start + offset
        image = Image.open(ROOT / "preview" / f"slide-{number:02}.png")
        assert image.size == (1600, 900), image.size
        image.thumbnail((800, 450))
        x, y = (offset % 2) * 800, (offset // 2) * 476
        sheet.paste(image, (x, y + 26))
        draw.text((x + 12, y + 6), f"Slide {number:02}", fill="#242424")
    sheet.save(QA / f"contact-{start:02}-{start+3:02}.png")

print("Verified 16 slides, matching speaker notes, talking points, PDF and 16 renders.")
print("Extracted text and four contact sheets saved to local qa directory.")
