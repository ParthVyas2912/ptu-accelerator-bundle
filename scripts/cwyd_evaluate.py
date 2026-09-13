"""Small staged real-application checks, never direct replacement RAG."""
import argparse
import json
from pathlib import Path
import time
import httpx

B = Path(r"C:\Users\partvyas\OneDrive - Microsoft\Desktop\projects\PTU accelerator Bundle")
E = B / "evidence" / "cwyd"
E.mkdir(parents=True, exist_ok=True)
API = "http://127.0.0.1:8112"


def call(name, method, path, **kwargs):
    start = time.perf_counter()
    try:
        response = httpx.request(method, API + path, timeout=240, **kwargs)
        try:
            actual = response.json()
        except ValueError:
            actual = response.text[:1000]
        result = {"test": name, "method": method, "path": path,
                  "status": response.status_code, "actual": actual,
                  "latency_ms": round((time.perf_counter()-start)*1000, 2)}
    except Exception as exc:
        result = {"test": name, "error_type": type(exc).__name__,
                  "latency_ms": round((time.perf_counter()-start)*1000, 2)}
    (E / (name + ".json")).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def upload(path):
    return call("upload-" + path.stem, "POST", "/api/admin/documents",
                files={"file": (path.name, path.read_bytes(), "text/plain")})


parser = argparse.ArgumentParser()
parser.add_argument("stage", choices=["health", "first-upload", "rest-upload", "questions", "update", "update-question", "blocked-chat"])
stage = parser.parse_args().stage
if stage == "health":
    call("health", "GET", "/api/health")
    call("documents", "GET", "/api/admin/documents")
elif stage == "blocked-chat":
    call("blocked-conversation", "POST", "/api/conversation",
         json={"messages": [{"role": "user", "content":
                             "What is the domestic meal allowance in the fictional Larkspur travel policy? Cite the source."}]})
elif stage == "first-upload":
    upload(B / "test-data" / "cwyd" / "ptu-cwyd-travel.txt")
elif stage == "rest-upload":
    for path in sorted((B / "test-data" / "cwyd").glob("*.txt")):
        if path.name != "ptu-cwyd-travel.txt":
            result = upload(path)
            if result.get("status") not in (200, 201, 202):
                break
elif stage == "questions":
    question = (
        "For fictional Larkspur Research Cooperative, answer these numbered questions "
        "separately, citing the relevant policy for every supported answer: "
        "1. What is the domestic meal allowance per travel day? "
        "2. What is the annual learning allowance? "
        "3. How many remote-work days are permitted each week? "
        "4. How long are calibration records retained? "
        "5. How often are shared field sensors calibrated? "
        "6. Compare the travel and learning claim submission deadlines, citing BOTH policies. "
        "7. What is the orbital relocation allowance? If it is absent from the policies, "
        "state that there is insufficient evidence; do not invent it."
    )
    call("questions-grouped", "POST", "/api/conversation",
         json={"messages": [{"role": "user", "content": question}]})
elif stage == "update":
    updated = (
        "FICTIONAL UNCLASSIFIED DEMONSTRATION POLICY\n"
        "Larkspur Research Cooperative — Travel Policy, version 2, active 2026-09-11.\n"
        "This version supersedes version 1. The domestic meal allowance is now 91 credits "
        "per travel day, replacing the previous 73 credits.\n"
        "Travel claims must be submitted within 21 calendar days of returning.\n"
    ).encode()
    call("upload-contradictory-update", "POST", "/api/admin/documents",
         files={"file": ("ptu-cwyd-travel.txt", updated, "text/plain")})
elif stage == "update-question":
    call("question-update", "POST", "/api/conversation",
         json={"messages": [{"role": "user", "content":
                             "What is the currently active domestic meal allowance at fictional "
                             "Larkspur Research Cooperative? A previous policy said 73 credits. "
                             "Cite the active source and explain whether it supersedes that amount."}]})
