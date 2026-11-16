"""Test bootstrap.

The build sandbox exports proxy variables (incl. an IPv6 NO_PROXY entry)
that httpx 0.27 misparses when any code constructs an httpx client at
import time (e.g. the legacy OpenAI client in app.workers). Stripping
them here keeps TestClient-based tests hermetic; production deployments
manage their own proxy configuration.
"""
import os

for _k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
           "http_proxy", "https_proxy", "all_proxy", "no_proxy"):
    os.environ.pop(_k, None)
