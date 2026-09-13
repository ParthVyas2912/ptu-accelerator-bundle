"""Run inside an official image with Docker --network none. No host port publish."""
import asyncio
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

component = sys.argv[1]
if component == "mcp":
    command = ["uv", "run", "python", "mcp_server.py", "--transport",
               "streamable-http", "--host", "0.0.0.0", "--port", "9000"]
    url = "http://127.0.0.1:9000/health"
elif component == "frontend":
    command = ["/usr/local/bin/uvicorn", "frontend_server:app", "--host", "0.0.0.0", "--port", "3000"]
    url = "http://127.0.0.1:3000/health"
elif component == "backend":
    command = ["/app/.venv/bin/python", "/eval/macae_cloud_run.py"]
    url = "http://127.0.0.1:8000/healthz"
else:
    raise ValueError(component)
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
try:
    result = {"component": component, "externalNetwork": "none", "publishedPorts": [], "modelRequests": 0}
    for _ in range(120):
        if process.poll() is not None:
            raise RuntimeError("Native CMD exited: " + process.communicate()[0].decode()[-3000:])
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                result["healthHttpStatus"] = response.status
                break
        except urllib.error.HTTPError as exc:
            result["healthHttpStatus"] = exc.code
            break
        except OSError:
            time.sleep(0.5)
    else:
        raise TimeoutError("Native image did not listen within 60 seconds")
    if component == "mcp":
        from fastmcp import Client
        async def check():
            async with Client("http://127.0.0.1:9000/hr/mcp") as client:
                tools = await client.list_tools()
                response = await client.call_tool("get_workflow_blueprint", {"workflow": "onboarding"})
                return {"toolCount": len(tools), "blueprintIsError": response.is_error}
        result.update(asyncio.run(check()))
        assert result["toolCount"] > 0 and not result["blueprintIsError"]
    elif component == "frontend":
        with urllib.request.urlopen("http://127.0.0.1:3000/") as response:
            html = response.read().decode()
            result["uiHttpStatus"] = response.status
            result["nativeTitlePresent"] = "Multi-Agent" in html
        assert result["healthHttpStatus"] == 200 and result["nativeTitlePresent"]
    else:
        result["inferenceEnabled"] = os.environ.get("MACAE_LIVE_REQUESTS_ENABLED", "false")
        assert result["healthHttpStatus"] == 200 and result["inferenceEnabled"] == "false"
    print("OFFLINE_CONTAINER_SMOKE " + json.dumps(result), flush=True)
finally:
    process.terminate()
    try:
        process.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
