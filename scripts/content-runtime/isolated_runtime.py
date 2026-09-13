"""Idle/disarmed by default; a bounded supervisor runs the original native entrypoint."""
import json
import os
from pathlib import Path
import runpy
import signal
import subprocess
import sys
import threading
import time

from azure.core.exceptions import ResourceNotFoundError
from content_guard import redact
import isolated_scope as scope


def worker():
    if os.environ.get("CONTENT_SCOPE_WORKER") != "1":
        raise RuntimeError("Scoped worker flag required")
    state = scope.read_control()
    if state["mode"] != "armed" or time.time() > state["deadline"]:
        raise RuntimeError("Run is disarmed or expired")
    scope.install()
    from cloud_entry import mongo_connection
    os.environ["APP_COSMOS_CONNSTR"] = mongo_connection()
    sys.path.insert(0, "/app/src")
    path = "/app/src/main.py" if os.environ["CONTENT_SERVICE"] == "processor" else "/app/src/main_service.py"
    runpy.run_path(path, run_name="__main__")


def supervisor():
    if os.environ.get("CONTENT_INFERENCE_DISARMED") != "1":
        raise RuntimeError("Supervisor must stay hard-disarmed")
    child = None
    logs = []
    shutdown = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: shutdown.set())
    signal.signal(signal.SIGINT, lambda *_: shutdown.set())
    try:
        while not shutdown.is_set():
            try:
                state = scope.read_control()
            except ResourceNotFoundError:
                state = {"mode": "disarmed"}
            armed = state["mode"] == "armed" and time.time() < state["deadline"]
            if armed and child is None:
                env = dict(os.environ, CONTENT_INFERENCE_DISARMED="0", CONTENT_SCOPE_WORKER="1",
                           MAX_RECEIVE_ATTEMPTS="100", RETRY_VISIBILITY_DELAY_SECONDS="3600")
                child = subprocess.Popen([sys.executable, __file__, "worker"], env=env, cwd="/app",
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         text=True, errors="replace", start_new_session=True)
                def capture():
                    for line in child.stdout:
                        text = redact(line.rstrip())
                        print(text, flush=True)
                        logs.append(text)
                        if len(logs) > 600:
                            logs.pop(0)
                threading.Thread(target=capture, daemon=True).start()
                scope.event("native-worker-started", pid=child.pid)
            if child is not None:
                scope.blob(f"evaluation/{scope.RUN}-{os.environ['CONTENT_SERVICE']}-logs.json").upload_blob(
                    json.dumps(logs), overwrite=True)
                if not armed:
                    break
                if child.poll() is not None:
                    scope.fail("Native worker exited; no automatic restart")
            shutdown.wait(3)
    finally:
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=10)
        if child is not None:
            scope.blob(f"evaluation/{scope.RUN}-{os.environ['CONTENT_SERVICE']}-logs.json").upload_blob(
                json.dumps(logs), overwrite=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["worker"]:
        worker()
    else:
        supervisor()
