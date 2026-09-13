"""Opt-in native evaluation guard. Never alters service response content."""
import os

if os.environ.get("CONTENT_NATIVE_GUARD") == "1":
    try:
        import content_guard
        content_guard.install()
    except BaseException:
        # Python otherwise ignores sitecustomize failures: fail CLOSED instead.
        os._exit(86)
