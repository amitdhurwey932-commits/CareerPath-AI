"""
Gunicorn configuration file for CareerPath AI — production deployments.

Usage:
    gunicorn -c gunicorn.conf.py wsgi:app

All tuneable values are read from environment variables so that the same
file works across different hosting environments without modification.
See .env.example for documentation on each variable.

References:
    https://docs.gunicorn.org/en/stable/settings.html
"""

import os
import multiprocessing

# ── Binding ───────────────────────────────────────────────────────────────────
# Managed platforms (Render, Railway, Heroku) inject a PORT environment variable
# and route public HTTPS traffic to that port through their own proxy layer.
# Gunicorn must bind to 0.0.0.0:$PORT so the platform can reach it.
#
# Self-managed servers (VPS + Nginx): set BIND=127.0.0.1:8000 in your .env so
# Gunicorn listens only on localhost and Nginx proxies to it.
#
# The default here covers the managed-platform case automatically.
_port = os.environ.get('PORT', '8000')
bind = os.environ.get('BIND', f'0.0.0.0:{_port}')

# ── Workers ───────────────────────────────────────────────────────────────────
# Sync workers are the safest default for Flask/SQLite.
# For I/O-heavy workloads, switch to worker_class = 'gevent' and
# add gevent to requirements.txt.
workers = int(os.environ.get('NUM_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'

# ── Timeouts ──────────────────────────────────────────────────────────────────
# Raise this if AI API calls take longer than 30 s (the default).
timeout = int(os.environ.get('WORKER_TIMEOUT', '60'))
graceful_timeout = 30
keepalive = 5

# ── Logging ───────────────────────────────────────────────────────────────────
# Log to stdout/stderr so the process supervisor (systemd, Docker, etc.) can
# capture and forward logs without extra configuration.
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ── Security ──────────────────────────────────────────────────────────────────
# Gunicorn honours this when deciding which IPs may set forwarded headers.
# Must match the IP of your Nginx proxy (127.0.0.1 for same-host Nginx,
# or '*' for managed platforms like Heroku / Render where the proxy IP varies).
forwarded_allow_ips = os.environ.get('FORWARDED_ALLOW_IPS', '127.0.0.1')

# Prevent information disclosure in HTTP response headers.
# https://docs.gunicorn.org/en/stable/settings.html#server-mechanics
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# ── Process naming ────────────────────────────────────────────────────────────
proc_name = 'careerpath-ai'
