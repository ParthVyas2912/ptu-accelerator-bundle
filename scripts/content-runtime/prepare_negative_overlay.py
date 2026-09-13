"""One-file negative test overlay on the verified recovery driver image."""
import ast
import os
from pathlib import Path
import shutil

root = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval/negative-api-r6"
root.mkdir(parents=True, exist_ok=True)
source = Path(__file__).parent / "negative_file.py"
ast.parse(source.read_text())
shutil.copy2(source, root / source.name)
(root / "Dockerfile").write_text(
    "FROM acrptubundle7d804f70.azurecr.io/content/eval-api@sha256:"
    "b215ba2c0103d6cc6abd5cf8175e822d33bc15c9fcdefae512dbe55f0df58906\n"
    "COPY negative_file.py /opt/content_eval/negative_file.py\n", encoding="utf-8")
print(root)
