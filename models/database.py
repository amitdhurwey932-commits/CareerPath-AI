import sqlite3
import os
from flask import g, current_app
from werkzeug.security import generate_password_hash


DATABASE_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    education_level TEXT,
    role TEXT NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    degree_course TEXT,
    interests TEXT,
    technical_skills TEXT,
    soft_skills TEXT,
    experience_level TEXT DEFAULT 'beginner',
    preferred_field TEXT,
    career_goals TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS career_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    career_key TEXT NOT NULL,
    match_score REAL,
    match_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    skill_level TEXT DEFAULT 'not_learned',
    category TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, skill_name)
);

CREATE TABLE IF NOT EXISTS learning_roadmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    career_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, career_key)
);

CREATE TABLE IF NOT EXISTS roadmap_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roadmap_id INTEGER NOT NULL,
    step_index INTEGER NOT NULL,
    topic TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    FOREIGN KEY (roadmap_id) REFERENCES learning_roadmaps(id) ON DELETE CASCADE,
    UNIQUE(roadmap_id, step_index)
);

CREATE TABLE IF NOT EXISTS project_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    project_key TEXT NOT NULL,
    status TEXT DEFAULT 'suggested',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, project_key)
);

CREATE TABLE IF NOT EXISTS interview_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    career_role TEXT NOT NULL,
    topic TEXT NOT NULL,
    difficulty TEXT DEFAULT 'beginner',
    question TEXT NOT NULL,
    user_answer TEXT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS resume_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


def get_db():
    """Get database connection, creating one if needed for this request."""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE_PATH'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialise database schema."""
    db = get_db()
    db.executescript(DATABASE_SCHEMA)
    db.commit()


def seed_admin():
    """Create a default admin user if none exists.

    Credentials are controlled by environment variables:
      ADMIN_USERNAME  — defaults to 'admin'
      ADMIN_EMAIL     — defaults to 'admin@careerpathAI.local'
      ADMIN_PASSWORD  — defaults to 'Admin@1234' (change in production!)
    """
    db = get_db()
    admin = db.execute(
        "SELECT id FROM users WHERE role = 'admin' LIMIT 1"
    ).fetchone()
    if not admin:
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@careerpathAI.local')
        password = os.environ.get('ADMIN_PASSWORD', 'Admin@1234')
        db.execute(
            """INSERT OR IGNORE INTO users (username, email, password_hash, education_level, role)
               VALUES (?, ?, ?, ?, ?)""",
            (
                username,
                email,
                generate_password_hash(password),
                'postgraduate',
                'admin',
            ),
        )
        db.commit()


def query_db(query, args=(), one=False):
    """Execute a SELECT query and return results."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    """Execute an INSERT/UPDATE/DELETE query."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid


def init_app(app):
    """Register database functions with Flask app."""
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
        seed_admin()
