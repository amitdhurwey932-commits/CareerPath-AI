import os
from datetime import timedelta


class Config:
    """Base configuration — values safe for all environments."""

    # ── Security ──────────────────────────────────────────────────────────────
    # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # ── Session cookies ───────────────────────────────────────────────────────
    # SESSION_COOKIE_SECURE is overridden per environment below.
    SESSION_COOKIE_HTTPONLY = True
    # 'Lax' allows the cookie to be sent on top-level navigations (e.g. OAuth
    # redirects).  Switch to 'Strict' if you never need cross-site navigation.
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # ── CSRF ──────────────────────────────────────────────────────────────────
    WTF_CSRF_ENABLED = True

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'careerpath.db')

    # ── AI API ────────────────────────────────────────────────────────────────
    AI_API_KEY = os.environ.get('AI_API_KEY', '')
    AI_API_URL = os.environ.get('AI_API_URL', 'https://api.openai.com/v1/chat/completions')
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')
    AI_DEMO_MODE = not bool(os.environ.get('AI_API_KEY', ''))


class DevelopmentConfig(Config):
    """Local development — runs on http://localhost:5000."""

    DEBUG = True
    # Do NOT set Secure on cookies in development; the browser won't send them
    # over plain HTTP and you'll be silently logged out on every request.
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production — must run behind an HTTPS reverse proxy."""

    DEBUG = False

    # Cookies must only travel over HTTPS.
    SESSION_COOKIE_SECURE = True

    # Tell Flask to trust the X-Forwarded-Proto header forwarded by the proxy
    # so that url_for() generates https:// URLs and redirects work correctly.
    # This is set here as a hint; the actual ProxyFix middleware is applied in
    # wsgi.py based on the PROXY_COUNT environment variable.
    PREFERRED_URL_SCHEME = 'https'

    # Gunicorn/uWSGI workers should not run as root; enforce production safety.
    PROPAGATE_EXCEPTIONS = False


class TestingConfig(Config):
    """Automated test suite — uses an in-memory database."""

    TESTING = True
    DEBUG = False
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    DATABASE_PATH = ':memory:'
    SECRET_KEY = 'test-secret-key-not-for-production'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
