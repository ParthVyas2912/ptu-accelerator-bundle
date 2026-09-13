"""Stage a bounded data-repair/recovery driver, preserving the original app."""
import ast
import os
from pathlib import Path
import shutil

root = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval/recovery-api-r5"
root.mkdir(parents=True, exist_ok=True)
for name in ("cloud_batch.py", "exercise_app.py"):
    source = Path(__file__).parent / name
    ast.parse(source.read_text())
    shutil.copy2(source, root / name)
(root / "Dockerfile").write_text(
    "FROM acrptubundle7d804f70.azurecr.io/content/eval-api@sha256:"
    "9e6b838c827291d46727f703f9369abd911a04af1bd16f13fe937ad92fffebb3\n"
    "COPY cloud_batch.py exercise_app.py /opt/content_eval/\n", encoding="utf-8")
print(root)
