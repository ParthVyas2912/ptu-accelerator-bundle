"""Derive config-only ARM repair; never touches network/storage/model resources."""
import json
import os
from pathlib import Path

root = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval"
template = json.loads((root / "content-native.json").read_text(encoding="utf-8"))
owner = "5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b"
resources = []
for resource in template["resources"]:
    if resource["type"].startswith("Microsoft.AppConfiguration/") or (
        resource["type"] == "Microsoft.Authorization/roleAssignments" and
        owner in str(resource.get("properties"))):
        resource["dependsOn"] = [dep for dep in resource.get("dependsOn", [])
                                 if "Microsoft.AppConfiguration/" in dep or owner in dep]
        resources.append(resource)
assert len(resources) == 3
assert resources[0]["name"] == "appcs-ptuv-content-260911"
assert resources[0]["properties"]["disableLocalAuth"] is True
assert resources[0]["properties"]["dataPlaneProxy"]["authenticationMode"] == "Pass-through"
template["resources"] = resources
template["outputs"] = {}
(root / "content-config-repair.json").write_text(json.dumps(template, indent=2), encoding="utf-8")
print("Prepared config-only repair: existing Standard store, Entra writer RBAC, nonsecret settings.")
