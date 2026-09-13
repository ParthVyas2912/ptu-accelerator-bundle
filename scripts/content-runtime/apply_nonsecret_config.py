"""Populate only the approved new AppConfig using Entra, after RBAC propagation."""
import csv
import json
import os
from pathlib import Path
import re
from azure.identity import AzureCliCredential
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting

root = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval"
variables = json.loads((root / "content-native.json").read_text())["variables"]


def resolve(value):
    if value == "[variables('openAiEndpoint')]":
        return resolve(variables["openAiEndpoint"])
    match = re.fullmatch(r"\[format\('([^']*)', (.*)\)\]", value)
    if match:
        args = next(csv.reader([match.group(2)], quotechar="'", skipinitialspace=True))
        return match.group(1).format(*args)
    if value.startswith("["):
        raise ValueError("Unrecognized ARM expression; refusing to guess configuration")
    return value


settings = {key: resolve(value) for key, value in variables["settings"].items()}
assert "APP_COSMOS_CONNSTR" not in settings
assert not any("mongodb://" in value for value in settings.values())
client = AzureAppConfigurationClient(
    "https://appcs-ptuv-content-260911.azconfig.io",
    AzureCliCredential(process_timeout=120),
    credential_scopes=["https://azconfig.io/.default"])
written = []
error = None
try:
    for key, value in settings.items():
        client.set_configuration_setting(ConfigurationSetting(
            key=key, value=value, content_type="text/plain"))
        written.append(key)
except Exception as exc:
    error = type(exc).__name__ + ": " + str(exc)[:1000]
result = {"writtenCount": len(written), "keys": written, "error": error,
          "authentication": "Entra AzureCliCredential", "secretValues": False}
path = Path(__file__).resolve().parents[2] / "evidence/content/native-config-repair.json"
path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"writtenCount": len(written), "error": error}))
