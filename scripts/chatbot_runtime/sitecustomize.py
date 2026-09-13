"""Opt-in, fail-closed metering for this accelerator's isolated Python processes."""
import os

if os.environ.get("CHATBOT_METERING") == "1":
    try:
        from chatbot_metering import install
        install()
    except Exception:
        # Python otherwise suppresses sitecustomize failures and continues.
        os._exit(78)
