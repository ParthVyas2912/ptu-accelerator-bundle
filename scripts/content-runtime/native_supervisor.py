"""Attached native launcher; runtime-only Mongo credential, four-GiB Windows job."""
import argparse
import ctypes
from ctypes import wintypes
import functools
import http.server
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import time

import psutil
from content_guard import redact

BUNDLE = Path(__file__).resolve().parents[2]
REPO = Path.home() / "OneDrive - Microsoft/Desktop/repo/content-processing-solution-accelerator"
ROOT = Path(os.environ["LOCALAPPDATA"]) / "ptu-content-eval"
STATE = ROOT / "native-state.json"
STOP = ROOT / "native-stop.json"
CHILDREN = []
STARTED = time.time()
PEAK_RSS = 0


def memory_job():
    """Hard aggregate committed-memory limit, inherited by all descendants."""
    class Basic(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD)]
    class IO(ctypes.Structure):
        _fields_ = [(x, ctypes.c_uint64) for x in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]
    class Extended(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", IO),
                    ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                             ctypes.c_void_p, wintypes.DWORD]
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    job = kernel.CreateJobObjectW(None, None)
    info = Extended()
    info.BasicLimitInformation.LimitFlags = 0x2000 | 0x200 | 0x400
    info.JobMemoryLimit = 4 * 1024 ** 3
    if not kernel.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not kernel.AssignProcessToJobObject(job, kernel.GetCurrentProcess()):
        raise ctypes.WinError(ctypes.get_last_error())
    return job


def save_state(status):
    STATE.write_text(json.dumps({
        "supervisorPid": os.getpid(), "supervisorCreated": psutil.Process().create_time(),
        "started": STARTED, "status": status, "memoryLimitBytes": 4 * 1024**3,
        "peakAggregateRssBytes": PEAK_RSS,
        "services": [{"name": name, "pid": proc.pid, "returnCode": proc.poll()}
                     for name, proc in CHILDREN],
        "api": "http://127.0.0.1:8113", "web": "http://127.0.0.1:5113",
    }, indent=2), encoding="utf-8")


def stop_owned():
    # Specific owned PIDs only; never a process-name kill.
    descendants = psutil.Process().children(recursive=True)
    for proc in reversed(descendants):
        try:
            proc.terminate()
        except psutil.Error:
            pass
    psutil.wait_procs(descendants, timeout=8)


def monitor():
    global PEAK_RSS
    while True:
        try:
            rss = sum(p.memory_info().rss for p in
                      [psutil.Process()] + psutil.Process().children(recursive=True)
                      if p.is_running())
            PEAK_RSS = max(PEAK_RSS, rss)
            if rss >= 4 * 1024**3 or psutil.virtual_memory().available < 1024**3:
                print("CONTENT_MEMORY_GUARD: aggregate/free-memory stop", flush=True)
                stop_owned()
                save_state("memory-guard-stopped")
                os._exit(87)
            if STOP.exists():
                stop = json.loads(STOP.read_text(encoding="utf-8-sig"))
                if stop.get("supervisorPid") == os.getpid() and stop.get("requested", 0) >= STARTED:
                    stop_owned()
                    save_state("stopped")
                    os._exit(0)
            save_state("running")
        except (psutil.Error, OSError, ValueError):
            pass
        time.sleep(1)


def log_pipe(name, stream):
    for line in iter(stream.readline, ""):
        print(f"[{name}] {redact(line.rstrip())}", flush=True)


def launch(name, command, cwd, env):
    service_env = env | {"CONTENT_SERVICE": name}
    proc = subprocess.Popen(command, cwd=cwd, env=service_env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    CHILDREN.append((name, proc))
    threading.Thread(target=log_pipe, args=(name, proc.stdout), daemon=True).start()
    print(f"CONTENT_STARTED service={name} pid={proc.pid}", flush=True)
    save_state("starting")
    return proc


def wait_alive(proc, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"Native service exited with code {proc.returncode}")
        time.sleep(1)


def mongo_secret():
    guard = str(BUNDLE / "Invoke-LabAz.ps1").replace("'", "''")
    command = (
        f"& '{guard}' -AzArguments @('cosmosdb','keys','list','--type','connection-strings',"
        "'--name','cosmos-ptuv-content-260911','--resource-group','rg-ptu-content-demo',"
        "'--subscription','1feb53b2-854a-4ea7-b5a6-709b7d804f70',"
        "'--query','connectionStrings[0].connectionString','-o','tsv')")
    result = subprocess.run(["pwsh", "-NoProfile", "-Command", command],
                            capture_output=True, text=True, timeout=90)
    value = result.stdout.strip()
    if result.returncode or not value.startswith("mongodb://"):
        raise RuntimeError("Mongo runtime credential retrieval failed; output suppressed")
    from urllib.parse import urlsplit
    if urlsplit(value).hostname != "cosmos-ptuv-content-260911.mongo.cosmos.azure.com":
        raise RuntimeError("Mongo runtime credential has an unapproved hostname")
    return value


def serve_web():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass
        def do_GET(self):
            # React history routing; assets retain ordinary 404 behavior.
            if "." not in self.path.rsplit("/", 1)[-1]:
                self.path = "/index.html"
            super().do_GET()
    directory = str(REPO / "src/ContentProcessorWeb/build")
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 5113), functools.partial(Handler, directory=directory))
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--web-only", action="store_true")
    args = parser.parse_args()
    if args.web_only:
        serve_web()
        return
    if psutil.virtual_memory().available < 5 * 1024**3:
        raise RuntimeError("Admission denied: need 5 GiB available before native startup")
    for port in (8113, 5113):
        with socket.socket() as check:
            if check.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"Port {port} is already occupied")
    job = memory_job()  # Keep handle alive until this attached supervisor exits.
    os.environ["APP_COSMOS_CONNSTR"] = mongo_secret()
    env = dict(os.environ)
    for key in ("AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_OPENAI_API_KEY",
                "OPENAI_API_KEY", "IDENTITY_ENDPOINT", "MSI_ENDPOINT",
                "WEBSITE_SITE_NAME", "KUBERNETES_SERVICE_HOST"):
        env.pop(key, None)
    env.update({
        "APP_ENV": "dev", "AZURE_TOKEN_CREDENTIALS": "AzureCliCredential",
        "APP_CONFIG_ENDPOINT": "https://appcs-ptuv-content-260911.azconfig.io",
        "APP_CONFIGURATION_URL": "https://appcs-ptuv-content-260911.azconfig.io",
        "CONTENT_NATIVE_GUARD": "1",
        "CONTENT_REQUEST_LEDGER": str(ROOT / "native-requests.sqlite"),
        "PYTHONPATH": str(Path(__file__).parent), "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1", "OTEL_SDK_DISABLED": "true",
        "APP_LOGGING_LEVEL": "WARNING", "CONCURRENT_WORKERS": "1",
        "MAX_RECEIVE_ATTEMPTS": "1", "RETRY_VISIBILITY_DELAY_SECONDS": "30",
    })
    poppler = ROOT / "poppler-release/poppler-26.07.0/Library/bin"
    if poppler.exists():
        env["PATH"] = str(poppler) + os.pathsep + env["PATH"]
    threading.Thread(target=monitor, daemon=True).start()
    api = launch("api", [str(ROOT / "api/Scripts/python.exe"), "-m", "uvicorn",
                        "app.main:app", "--host", "127.0.0.1", "--port", "8113",
                        "--no-access-log"], REPO / "src/ContentProcessorAPI", env)
    import urllib.request
    for _ in range(120):
        wait_alive(api, 1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:8113/health", timeout=2) as response:
                if response.status == 200:
                    break
        except (OSError, ValueError):
            pass
    else:
        raise RuntimeError("API health did not become ready within startup bound")
    processor = launch("processor", [str(ROOT / "processor/Scripts/python.exe"),
                                    "main.py"], REPO / "src/ContentProcessor/src", env)
    wait_alive(processor, 20)
    workflow = launch("workflow", [str(ROOT / "workflow/Scripts/python.exe"),
                                  "main_service.py"], REPO / "src/ContentProcessorWorkflow/src", env)
    wait_alive(workflow, 20)
    web = launch("web", [str(ROOT / "api/Scripts/python.exe"), str(Path(__file__)),
                         "--web-only"], REPO / "src/ContentProcessorWeb", env)
    wait_alive(web, 3)
    print("CONTENT_NATIVE_READY api=127.0.0.1:8113 web=127.0.0.1:5113", flush=True)
    while True:
        for name, proc in CHILDREN:
            if proc.poll() is not None:
                raise RuntimeError(f"{name} exited with {proc.returncode}")
        time.sleep(2)


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        print("CONTENT_NATIVE_STOP: " + redact(type(exc).__name__ + ": " + str(exc)), flush=True)
        stop_owned()
        save_state("failed")
        sys.exit(1)
