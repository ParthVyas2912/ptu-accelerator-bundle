"""Exercise the real single-file pipeline with the already prepared corrupt PDF."""
import json
import os
from pathlib import Path
import sys
import time

import exercise_app as app
from cloud_batch import export, read, save
from content_guard import redact


def main():
    if "negativeSingleFile" in app.DATA:
        raise RuntimeError("Submission intent already exists; refusing duplicate corrupt-file processing")
    before = read("content-call-budget.json")["requests"]
    before_models = sum(item["kind"] == "model" for item in before)
    app.DATA["negativeSingleFile"] = {"submissionAttempted": True}
    app.save()
    path = Path(os.environ["CONTENT_FIXTURE_ROOT"]) / "content/corrupt/truncated.pdf"
    with path.open("rb") as stream:
        accepted = app.request("POST", "/contentprocessor/submit", expected=202,
            data={"data": json.dumps({"Schema_Id": app.DATA["schemas"]["autoclaim.json"],
                                      "Metadata_Id": "PTU-CONTENT-CORRUPT-SINGLE"})},
            files={"file": ("truncated.pdf", stream, "application/pdf")})
    process_id = accepted["process_id"]
    app.DATA["negativeSingleFile"]["processId"] = process_id
    app.save()
    result = {"processId": process_id, "endpoint": "/contentprocessor/submit",
              "acceptedStatus": 202, "polls": [], "modelAttemptsBefore": before_models}
    for _ in range(30):
        value = app.request("GET", f"/contentprocessor/status/{process_id}",
                            expected=(200, 302, 500), allow_redirects=False)
        status = app.DATA["apiCalls"][-1]["status"]
        result["polls"].append({"httpStatus": status, "value": value})
        save("negative-content-result.json", result)
        if status in (302, 500):
            result["terminalHttpStatus"] = status
            break
        time.sleep(3)
    else:
        result["pollingDeadlineReached"] = True
    result["steps"] = app.request(
        "GET", f"/contentprocessor/processed/{process_id}/steps", expected=None)
    rows = read("content-call-budget.json")["requests"]
    result["modelAttemptsAfter"] = sum(item["kind"] == "model" for item in rows)
    result["newRequests"] = rows[len(before):]
    result["passed"] = result.get("terminalHttpStatus") == 500 and (
        result["modelAttemptsAfter"] == before_models)
    app.DATA["negativeSingleFile"]["result"] = result
    app.save()
    save("negative-content-result.json", result)
    return {"negative": result, "evidence": export()}


if __name__ == "__main__":
    try:
        output = main()
    except Exception as exc:
        output = {"error": {"type": type(exc).__name__, "message": redact(exc)},
                  "evidence": export()}
        print("CONTENT_BATCH_JSON=" + json.dumps(output), flush=True)
        sys.exit(1)
    print("CONTENT_BATCH_JSON=" + json.dumps(output), flush=True)
