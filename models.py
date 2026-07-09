"""Database initialization and helper functions.

Uses raw sqlite3 with dictionary row factory for simplicity.
"""

import sqlite3
import os
from config import DATABASE_PATH, UPLOAD_FOLDER, THUMBNAIL_FOLDER


def get_db():
    """Get a database connection. Reuses connection within a Flask request."""
    try:
        from flask import g, has_app_context
        if has_app_context() and 'db' in g:
            return g.db
    except RuntimeError:
        pass

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        conn.execute("PRAGMA cache_size=-8000")
        conn.execute("PRAGMA mmap_size=268435456")
    except:
        pass

    # Store on g if in Flask context
    try:
        from flask import g, has_app_context
        if has_app_context():
            g.db = conn
    except RuntimeError:
        pass

    return conn


def close_db(exception=None):
    """Close the database connection at the end of a request."""
    from flask import g
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database tables and required directories."""
    # Ensure directories exist
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL DEFAULT '',
            major TEXT NOT NULL DEFAULT '',
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            phone TEXT NOT NULL DEFAULT '',
            qq TEXT DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # Add major column if upgrading from older schema
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN major TEXT NOT NULL DEFAULT ''")
    except:
        pass

    # Add award_tier and credits columns for older schema
    try:
        cursor.execute("ALTER TABLE submissions ADD COLUMN award_tier TEXT NOT NULL DEFAULT '国家级'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE submissions ADD COLUMN credits INTEGER NOT NULL DEFAULT 0")
    except:
        pass

    # Add must_change_password for batch-imported students
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0")
    except:
        pass

    # Competition catalog table (2026 discipline competition catalog)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competition_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            short_name TEXT DEFAULT '',
            category TEXT NOT NULL DEFAULT '学科竞赛',
            level TEXT NOT NULL DEFAULT '校级',
            organizer TEXT DEFAULT '',
            is_key_competition INTEGER NOT NULL DEFAULT 0,
            sort_order INTEGER NOT NULL DEFAULT 0,
            year INTEGER NOT NULL DEFAULT 2026,
            notes TEXT DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Submissions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            catalog_id INTEGER NOT NULL,
            award_level TEXT NOT NULL,
            award_tier TEXT NOT NULL DEFAULT '国家级',
            credits INTEGER NOT NULL DEFAULT 0,
            award_title TEXT DEFAULT '',
            team_name TEXT DEFAULT '',
            team_members TEXT DEFAULT '',
            is_leader INTEGER NOT NULL DEFAULT 1,
            award_date TEXT NOT NULL,
            certificate_image TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            review_comment TEXT DEFAULT '',
            reviewed_by INTEGER DEFAULT NULL,
            reviewed_at TEXT DEFAULT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (catalog_id) REFERENCES competition_catalog(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        )
    """)

    # Submission audit logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submission_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            old_status TEXT DEFAULT NULL,
            new_status TEXT DEFAULT NULL,
            performed_by INTEGER NOT NULL,
            comment TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (submission_id) REFERENCES submissions(id),
            FOREIGN KEY (performed_by) REFERENCES users(id)
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_student_id ON users(student_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON submissions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_catalog_id ON submissions(catalog_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submission_logs_submission_id ON submission_logs(submission_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_competition_catalog_level ON competition_catalog(level)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_competition_catalog_category ON competition_catalog(category)")

    conn.commit()
    conn.close()


def query_db(query, args=(), one=False):
    """Execute a SELECT query and return results."""
    conn = get_db()
    try:
        cur = conn.execute(query, args)
        rows = cur.fetchall()
        if one:
            return rows[0] if rows else None
        return rows
    except Exception:
        raise


def execute_db(query, args=()):
    """Execute an INSERT/UPDATE/DELETE query and return the lastrowid."""
    conn = get_db()
    try:
        cur = conn.execute(query, args)
        conn.commit()
        last_id = cur.lastrowid
        return last_id
    except Exception:
        raise
