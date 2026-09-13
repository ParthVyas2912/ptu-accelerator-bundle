"""MCAPS lab instrumentation for StepFly.

Wraps the OpenAI-compatible chat.completions.create call to satisfy the
continuation TEST AND MEASUREMENT CONTRACT:
  - per-attempt telemetry captured before SDK flattening
  - hard provider-attempt budget that stops the run rather than exceeding it

Never writes credentials. Only endpoint, model, ids, tokens and timings.
"""
import json
import os
import time
import uuid
from datetime import datetime, timezone

import openai
from openai.resources.chat.completions import Completions

BUDGET = int(os.environ.get("LAB_ATTEMPT_BUDGET", "0"))
if os.environ.get("LAB_ALLOW_PROVIDER_CALLS") != "1":
    BUDGET = 0
LEDGER = os.environ.get("LAB_LEDGER", "lab-ledger.jsonl")
RUN_ID = os.environ.get("LAB_RUN_ID", str(uuid.uuid4())[:8])
# StepFly spawns each Executor as a separate OS process, so an in-process
# counter is not a portfolio budget. The counter below is shared on disk.
COUNTER = os.environ.get("LAB_COUNTER", LEDGER + ".counter")

_state = {"attempts": 0}


class LabBudgetExceeded(RuntimeError):
    pass


def _acquire():
    lock = COUNTER + ".lock"
    for _ in range(2000):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            return fd, lock
        except FileExistsError:
            time.sleep(0.01)
    raise RuntimeError("Could not acquire lab budget lock")


def _release(fd, lock):
    os.close(fd)
    try:
        os.remove(lock)
    except OSError:
        pass


def _reserve():
    """Atomically reserve one global provider attempt across all processes."""
    fd, lock = _acquire()
    try:
        used = 0
        if os.path.exists(COUNTER):
            try:
                used = int(open(COUNTER, encoding="utf8").read().strip() or 0)
            except ValueError:
                used = 0
        if used >= BUDGET:
            raise LabBudgetExceeded(
                f"Global provider-attempt budget {BUDGET} reached; stopped before attempt {used + 1}."
            )
        used += 1
        with open(COUNTER, "w", encoding="utf8") as fh:
            fh.write(str(used))
        return used
    finally:
        _release(fd, lock)


def global_attempts():
    if os.path.exists(COUNTER):
        try:
            return int(open(COUNTER, encoding="utf8").read().strip() or 0)
        except ValueError:
            return 0
    return 0


def _write(record):
    fd, lock = _acquire()
    try:
        with open(LEDGER, "a", encoding="utf8") as fh:
            fh.write(json.dumps(record) + "\n")
    finally:
        _release(fd, lock)


_original_create = Completions.create


def _patched_create(self, *args, **kwargs):
    attempt = _reserve()
    _state["attempts"] += 1
    correlation = f"{RUN_ID}-{attempt:03d}"
    base = str(getattr(self._client, "base_url", ""))
    started = time.perf_counter()
    record = {
        "run_id": RUN_ID,
        "attempt": attempt,
        "pid": os.getpid(),
        "correlation_id": correlation,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": base,
        "requested_model": kwargs.get("model"),
        "stream": bool(kwargs.get("stream")),
        "max_tokens": kwargs.get("max_tokens"),
        "temperature": kwargs.get("temperature"),
        "request_message_count": len(kwargs.get("messages") or []),
        "request_chars": sum(len(str(m.get("content", ""))) for m in (kwargs.get("messages") or [])),
    }
    try:
        result = _original_create(self, *args, **kwargs)
    except Exception as exc:  # capture raw provider failure shape
        record.update({
            "outcome": "exception",
            "exception_type": type(exc).__name__,
            "http_status": getattr(exc, "status_code", None),
            "provider_error_code": getattr(getattr(exc, "body", None), "get", lambda k, d=None: None)("code", None)
            if isinstance(getattr(exc, "body", None), dict) else None,
            "message": str(exc)[:600],
            "client_elapsed_s": round(time.perf_counter() - started, 4),
        })
        _write(record)
        raise

    if record["stream"]:
        return _wrap_stream(result, record, started)

    _finish(record, result, started, ttft=None)
    return result


def _finish(record, result, started, ttft):
    usage = getattr(result, "usage", None)
    ptd = getattr(usage, "prompt_tokens_details", None) if usage else None
    ctd = getattr(usage, "completion_tokens_details", None) if usage else None
    choice = (getattr(result, "choices", None) or [None])[0]
    record.update({
        "outcome": "response",
        "http_status": 200,
        "provider_response_id": getattr(result, "id", None),
        "served_model": getattr(result, "model", None),
        "system_fingerprint": getattr(result, "system_fingerprint", None),
        "finish_reason": getattr(choice, "finish_reason", None) if choice else None,
        "refusal": getattr(getattr(choice, "message", None), "refusal", None) if choice else None,
        "content_filter_results": _safe(getattr(choice, "content_filter_results", None)) if choice else None,
        "prompt_filter_results": _safe(getattr(result, "prompt_filter_results", None)),
        "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage else None,
        "completion_tokens": getattr(usage, "completion_tokens", None) if usage else None,
        "total_tokens": getattr(usage, "total_tokens", None) if usage else None,
        "cached_tokens": getattr(ptd, "cached_tokens", None) if ptd else None,
        "reasoning_tokens": getattr(ctd, "reasoning_tokens", None) if ctd else None,
        "ttft_s": ttft,
        "client_elapsed_s": round(time.perf_counter() - started, 4),
        "response_chars": len(getattr(getattr(choice, "message", None), "content", "") or "") if choice else 0,
    })
    _write(record)


def _safe(obj):
    try:
        if obj is None:
            return None
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        return json.loads(json.dumps(obj, default=str))
    except Exception:
        return str(obj)[:300]


def _wrap_stream(stream, record, started):
    def gen():
        ttft = None
        chars = 0
        last = None
        usage = None
        try:
            for chunk in stream:
                last = chunk
                if getattr(chunk, "usage", None):
                    usage = chunk.usage
                ch = (getattr(chunk, "choices", None) or [None])[0]
                delta = getattr(ch, "delta", None) if ch else None
                if delta is not None and getattr(delta, "content", None):
                    if ttft is None:
                        ttft = round(time.perf_counter() - started, 4)
                    chars += len(delta.content)
                yield chunk
        finally:
            record.update({
                "outcome": "stream",
                "http_status": 200,
                "provider_response_id": getattr(last, "id", None),
                "served_model": getattr(last, "model", None),
                "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage else None,
                "completion_tokens": getattr(usage, "completion_tokens", None) if usage else None,
                "total_tokens": getattr(usage, "total_tokens", None) if usage else None,
                "cached_tokens": getattr(getattr(usage, "prompt_tokens_details", None), "cached_tokens", None)
                if usage else None,
                "ttft_s": ttft,
                "client_elapsed_s": round(time.perf_counter() - started, 4),
                "response_chars": chars,
            })
            _write(record)

    return gen()


def install():
    if getattr(Completions.create, "_lab_patched", False):
        return
    _patched_create._lab_patched = True
    Completions.create = _patched_create
    print(f"[lab] instrumentation active run_id={RUN_ID} budget={BUDGET} ledger={LEDGER}")


def attempts():
    return _state["attempts"]
