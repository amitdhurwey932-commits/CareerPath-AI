"""
WSGI entry point for production deployment.

Usage:
    gunicorn wsgi:app
    gunicorn -c gunicorn.conf.py wsgi:app

Environment variables must be set before starting (see .env.example).
Do NOT use Flask's built-in development server in production.

Proxy handling
--------------
When the app runs behind a single reverse proxy (Nginx, Caddy, etc.) set:

    FORWARDED_ALLOW_IPS=127.0.0.1   # IP of the proxy; use * only on platforms
                                     # such as Heroku where the proxy IP is dynamic
    PROXY_COUNT=1                    # number of proxy hops (almost always 1)

ProxyFix rewrites REMOTE_ADDR, X-Forwarded-For, and X-Forwarded-Proto so that
Flask sees the real client IP and generates https:// URLs correctly.
Do NOT set FORWARDED_ALLOW_IPS when there is no proxy in front of the app
(e.g. local development) — it would let any client spoof their IP.
"""

import os
from app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'production'))

# ── Trusted proxy middleware ────────────────────────────────────────────────
# Apply only when the app is deployed behind a reverse proxy.
# PROXY_COUNT must equal the number of actual proxy hops (usually 1).
# FORWARDED_ALLOW_IPS restricts which source IPs may set forwarded headers.
_proxy_count = int(os.environ.get('PROXY_COUNT', '0'))
if _proxy_count > 0:
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=_proxy_count,
        x_proto=_proxy_count,
        x_host=_proxy_count,
        x_prefix=_proxy_count,
    )
