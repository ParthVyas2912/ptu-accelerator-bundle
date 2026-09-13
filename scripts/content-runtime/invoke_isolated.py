"""Single authenticated exec with persistent raw-result capture; no automatic retry."""
import argparse
import datetime
import json
from pathlib import Path
import re
import subprocess
from content_guard import redact

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=("prepare", "run", "export", "disarm"))
args = parser.parse_args()
bundle = Path(__file__).resolve().parents[2]
command = f"/app/.venv/bin/python /opt/content_eval/isolated_driver.py {args.action}"
azargs = ["containerapp", "exec", "-g", "rg-ptu-content-demo", "-n", "ca-ptu-content-api",
          "--subscription", "1feb53b2-854a-4ea7-b5a6-709b7d804f70", "--command", command]
quoted = ",".join("'" + item.replace("'", "''") + "'" for item in azargs)
proc = subprocess.run(["pwsh", "-NoProfile", "-Command",
                       f"& '{bundle / 'Invoke-LabAz.ps1'}' -AzArguments @({quoted})"],
                      capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=780)
raw = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", proc.stdout)
marker = "CONTENT_ISOLATED_JSON="
evidence = bundle / "evidence" / "content"
if marker not in raw:
    (evidence / f"isolated-{args.action}-exec-error.json").write_text(
        json.dumps({"code": proc.returncode, "diagnostic": redact(raw[-12000:] + proc.stderr[-2000:])}),
        encoding="utf-8")
    raise RuntimeError("No result marker; see saved exec error. Respect any Retry-After; never rearm automatically.")
data = json.JSONDecoder().raw_decode(raw.split(marker, 1)[1].lstrip())[0]
data["capturedUtc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
data["controlPlaneExitCode"] = proc.returncode
path = evidence / f"isolated-{args.action}-result.json"
path.write_text(json.dumps(data, indent=2), encoding="utf-8")
print(json.dumps({"file": str(path), "claimId": data.get("claimId") or data.get("control", {}).get("claimId"),
                  "error": data.get("error"), "mode": data.get("mode") or data.get("control", {}).get("mode"),
                  "models": sum(row["kind"] == "model" for row in data["ledger"]["requests"]) if "ledger" in data else None,
                  "nativeStatus": data.get("claimDetail", {}).get("data", {}).get("status")}, indent=2))
if proc.returncode or data.get("error"):
    raise SystemExit(1)
