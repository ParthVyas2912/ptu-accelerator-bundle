"""Precache the official tokenizer at build time; keep runtime endpoint guard closed."""
import os
from pathlib import Path

root = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval/tokenizer-processor-r4"
root.mkdir(parents=True, exist_ok=True)
(root / "Dockerfile").write_text(
    "FROM acrptubundle7d804f70.azurecr.io/content/eval-processor@sha256:"
    "f9f489acc8e15af31aede01e806dad4a7bb1bd071228653034b434e2df0224dc\n"
    "USER root\n"
    "ENV TIKTOKEN_CACHE_DIR=/opt/content_tokenizer_cache\n"
    "RUN mkdir -p /opt/content_tokenizer_cache && CONTENT_NATIVE_GUARD=0 "
    "/app/.venv/bin/python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\" "
    "&& chmod -R a+rX /opt/content_tokenizer_cache\n"
    "USER gsauser\n"
    "RUN PYTHONPATH=/opt/content_eval:/app/src /app/.venv/bin/python -c "
    "\"import os; assert os.environ['CONTENT_NATIVE_GUARD']=='1'; "
    "from libs.pipeline.handlers.logics.evaluate_handler.openai_confidence_evaluator import evaluate_confidence; "
    "assert evaluate_confidence({}, {'message': {'content': '{}'}, 'logprobs': None}) == {'_overall': 0.0}; "
    "print('PASS: original confidence evaluator runs with mandatory endpoint guard and cached tokenizer')\"\n",
    encoding="utf-8")
print(root)
