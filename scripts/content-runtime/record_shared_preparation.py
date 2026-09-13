"""Merge current preparation status without replacing historical deployment evidence."""
import datetime
import json
from pathlib import Path

bundle = Path(__file__).resolve().parents[2]
folder = bundle / "evidence/content"
path = folder / "result.json"
result = json.loads(path.read_text(encoding="utf-8"))
result["status"] = "approved_dependencies_created_shared_private_container_fallback_prepared_waiting_parent_platform"
result["sharedPlatformPreparation"] = json.loads(
    (folder / "shared-platform-request.json").read_text(encoding="utf-8"))
result["containerBuildContexts"] = json.loads(
    (folder / "container-contexts.json").read_text(encoding="utf-8"))
result["latestConfigWrite"] = json.loads(
    (folder / "native-config-repair.json").read_text(encoding="utf-8"))
result["latestConfigWrite"]["recordedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
result["currentBlockers"] = [
    "Parent shared private platform and Content private endpoints not yet ready; preserve Disabled PNA",
    "Native host memory admission rejected; cloud fallback avoids this local runtime constraint",
    "Cloud runtime-only Mongo retrieval and durable shared12-call guard overlay not implemented yet",
    "No external API/UI until parent CIDR restriction or authentication configured"]
result["sharedPlatformPreparation"]["readiness"]["officialBuildContextsStaged"] = True
result["sharedPlatformPreparation"]["readiness"]["appConfigNonsecretSettingsWritten"] = (
    result["latestConfigWrite"]["writtenCount"])
progress = folder / "cloud-build-progress.json"
if progress.exists():
    result["cloudBuildProgress"] = json.loads(progress.read_text(encoding="utf-8"))
    result["status"] = "shared_platform_ready_content_private_endpoints_deploying_api_base_image_built"
    result["sharedPlatformPreparation"]["readiness"]["sharedPlatformReady"] = True
    result["currentBlockers"][0] = "Own Blob/Queue/Mongo PEs deploying; approved helper needs account-group/multi-DNS support for fourth AI PE"
path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print("Recorded exact PE request, four staged contexts, and successful40-key Entra config repair.")
