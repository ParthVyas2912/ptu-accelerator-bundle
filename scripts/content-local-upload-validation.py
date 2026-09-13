"""Exercise the accelerator's real upload validator, not a replacement service."""
import asyncio
import json
from pathlib import Path
import sys
import time

BUNDLE = Path(__file__).resolve().parents[1]
REPO = BUNDLE.parent.parent / "repo" / "content-processing-solution-accelerator"
sys.path.insert(0, str(REPO / "src" / "ContentProcessorAPI"))

from starlette.datastructures import Headers, UploadFile
from app.utils.upload_validation import validate_upload_for_processing


async def main():
    rows = []
    folder = BUNDLE / "test-data" / "content" / "corrupt"
    for name, content_type, expected in [
        ("unsupported.txt", "text/plain", 415),
        ("bad-magic.pdf", "application/pdf", 415),
        ("truncated.pdf", "application/pdf", "requires downstream parse"),
    ]:
        path = folder / name
        started = time.perf_counter()
        with path.open("rb") as stream:
            upload = UploadFile(file=stream, filename=name, size=path.stat().st_size,
                                headers=Headers({"content-type": content_type}))
            result = await validate_upload_for_processing(upload=upload, max_filesize_mb=20)
        rows.append({
            "file": name, "expected": expected,
            "actualStatus": getattr(result, "status_code", None),
            "acceptedForDownstreamProcessing": isinstance(result, tuple),
            "latencyMs": round((time.perf_counter() - started) * 1000, 3),
            "networkRequests": 0,
            "scope": "direct production validator function; NOT HTTP endpoint or end-to-end processing",
        })
    evidence = BUNDLE / "evidence" / "content"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "local-upload-validation.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps(rows, indent=2))


asyncio.run(main())
