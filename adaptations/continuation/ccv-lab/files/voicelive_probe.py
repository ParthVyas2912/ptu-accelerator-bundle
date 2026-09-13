"""Bounded, telephony-free Azure Voice Live probe.

Proves (or disproves) that the Call Center Voice accelerator's core dependency
-- the Voice Live realtime session -- is reachable in this lab subscription
using Entra auth, without PSTN, ACS, or a browser microphone.

Emits full per-attempt telemetry per the measurement contract.
"""
import asyncio, json, os, sys, time, uuid, datetime, traceback

from azure.identity.aio import AzureCliCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    RequestSession, Modality, InputAudioFormat, OutputAudioFormat,
    ServerEventType, UserMessageItem, InputTextContentPart,
)

if (os.environ.get("LAB_ALLOW_PROVIDER_CALLS") != "1"
        or int(os.environ.get("VL_MAX_ATTEMPTS", "0")) <= 0):
    raise SystemExit("Archived harness is disarmed; provider execution requires separate approval.")

ENDPOINT = os.environ["AZURE_VOICE_LIVE_ENDPOINT"]
MODEL = os.environ.get("VOICE_LIVE_MODEL", "gpt-4o-mini")
OUT = os.environ["OUT"]
PROMPT = os.environ.get(
    "VL_PROMPT",
    "A customer says their account was double-charged 240 dollars last Tuesday. "
    "In two sentences, acknowledge and state the single next step you will take.",
)
MAX_ATTEMPTS = int(os.environ.get("VL_MAX_ATTEMPTS", "0"))


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


async def probe(attempt: int, rec: dict):
    cred = AzureCliCredential()
    t0 = time.perf_counter()
    try:
        async with connect(endpoint=ENDPOINT, credential=cred, model=MODEL) as conn:
            rec["connect_seconds"] = round(time.perf_counter() - t0, 3)
            rec["connected"] = True

            await conn.session.update(session=RequestSession(
                modalities=[Modality.TEXT],
                instructions="You are a concise call center agent.",
                input_audio_format=InputAudioFormat.PCM16,
                output_audio_format=OutputAudioFormat.PCM16,
            ))
            await conn.conversation.item.create(
                item=UserMessageItem(content=[InputTextContentPart(text=PROMPT)])
            )
            await conn.response.create()

            ttft = None
            text = []
            deadline = time.perf_counter() + 60
            async for ev in conn:
                et = ev.type
                rec["events"].append(str(et))
                if et == ServerEventType.SESSION_CREATED:
                    rec["session_id"] = getattr(getattr(ev, "session", None), "id", None)
                elif et == ServerEventType.RESPONSE_TEXT_DELTA:
                    if ttft is None:
                        ttft = round(time.perf_counter() - t0, 3)
                    text.append(getattr(ev, "delta", "") or "")
                elif et == ServerEventType.RESPONSE_TEXT_DONE:
                    text.append("")
                elif et == ServerEventType.RESPONSE_DONE:
                    r = getattr(ev, "response", None)
                    rec["response_id"] = getattr(r, "id", None)
                    rec["response_status"] = str(getattr(r, "status", None))
                    u = getattr(r, "usage", None)
                    if u is not None:
                        rec["usage"] = {
                            k: getattr(u, k, None)
                            for k in ("total_tokens", "input_tokens", "output_tokens")
                        }
                    if r is not None and getattr(r, "output", None):
                        for item in r.output:
                            for c in (getattr(item, "content", None) or []):
                                t = getattr(c, "text", None) or getattr(c, "transcript", None)
                                if t:
                                    text.append(t)
                    break
                elif et == ServerEventType.ERROR:
                    rec["provider_error"] = str(getattr(ev, "error", None))
                    break
                if time.perf_counter() > deadline:
                    rec["timeout"] = True
                    break

            rec["ttft_seconds"] = ttft
            rec["output_text"] = "".join(text).strip()
            rec["ok"] = bool(rec.get("output_text")) and not rec.get("provider_error")
    except Exception as exc:
        rec["connected"] = rec.get("connected", False)
        rec["exception_type"] = type(exc).__name__
        rec["exception"] = str(exc)[:2000]
        rec["status_code"] = getattr(exc, "status_code", None)
        rec["traceback"] = traceback.format_exc()[-2000:]
        rec["ok"] = False
    finally:
        rec["elapsed_seconds"] = round(time.perf_counter() - t0, 3)
        await cred.close()


async def main():
    ledger = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        rec = {
            "timestamp": now(),
            "stage": "voice-live-session-probe",
            "attempt": attempt,
            "correlation_id": str(uuid.uuid4()),
            "endpoint": ENDPOINT,
            "model": MODEL,
            "sdk": "azure-ai-voicelive",
            "auth": "AzureCliCredential (Entra, keyless)",
            "prompt": PROMPT,
            "events": [],
        }
        await probe(attempt, rec)
        ledger.append(rec)
        print(json.dumps({k: v for k, v in rec.items()
                          if k not in ("traceback", "events")}, indent=2)[:1800])
        if rec.get("ok"):
            break
        await asyncio.sleep(2)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)
    print(f"\nwritten: {OUT}  attempts={len(ledger)}  ok={any(r.get('ok') for r in ledger)}")


asyncio.run(main())
