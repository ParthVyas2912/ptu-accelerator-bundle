"""Render upstream, nonsecret DKM dev configuration; never obtain credentials."""
from pathlib import Path
import argparse

p = argparse.ArgumentParser()
p.add_argument("--repo", type=Path, required=True)
p.add_argument("--appconfig-endpoint", required=True)
a = p.parse_args()
if not a.appconfig_endpoint.startswith("https://appcs-dkmeval0911a.azconfig.io"):
    raise SystemExit("Refusing unexpected App Configuration endpoint")
root = a.repo
for component, target in (
    ("aiservice", "App/backend-api/Microsoft.GS.DPS.Host/appsettings.Development.json"),
    ("kernelmemory", "App/kernel-memory/service/Service/appsettings.Development.json"),
):
    text = (root / f"Deployment/appconfig/{component}/appsettings.Development.json.template").read_text(encoding="utf-8-sig")
    text = text.replace("{{ appconfig-url }}", a.appconfig_endpoint)
    # Supported configuration controls prevent SDK/queue amplification of the
    # small live-model budget. No application or inference implementation change.
    text = text.replace('"MaxRetries": 10', '"MaxRetries": 0')
    # This implementation compares DequeueCount <= threshold; initial count is1.
    # Allow the first delivery, then poison instead of retrying the handler.
    text = text.replace('"MaxRetriesBeforePoisonQueue": 20', '"MaxRetriesBeforePoisonQueue": 1')
    text = text.replace('"Default": "Trace"', '"Default": "Information"')
    text = text.replace('"Microsoft.AspNetCore": "Trace"', '"Microsoft.AspNetCore": "Warning"')
    (root / target).write_text(text, encoding="utf-8")
    print(f"Rendered upstream {component} runtime configuration; no credentials.")
text = (root / "Deployment/appconfig/frontapp/.env.template").read_text(encoding="utf-8-sig")
text = text.replace("{{ backend-fqdn }}", "/backend")
(root / "App/frontend-app/.env").write_text(text, encoding="utf-8")
print("Rendered upstream relative frontend proxy configuration; ClusterIP/loopback access only.")
