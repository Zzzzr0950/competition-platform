"""Application configuration constants."""

import os
import secrets

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask secret key for session signing
# IMPORTANT: On PythonAnywhere, set this as an environment variable in the Web tab,
# otherwise every app reload generates a new key and invalidates all user sessions.
_SECRET_FILE = os.path.join(BASE_DIR, '.secret_key')
_SECRET_ENV = os.environ.get('SECRET_KEY', '').strip()
if _SECRET_ENV:
    SECRET_KEY = _SECRET_ENV
elif os.path.exists(_SECRET_FILE):
    with open(_SECRET_FILE, 'r') as f:
        SECRET_KEY = f.read().strip()
else:
    SECRET_KEY = secrets.token_hex(32)
    with open(_SECRET_FILE, 'w') as f:
        f.write(SECRET_KEY)

# Database
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'platform.db')

# Upload settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'certificates')
THUMBNAIL_FOLDER = os.path.join(BASE_DIR, 'uploads', 'thumbnails')
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

# Session
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

# Pagination
ITEMS_PER_PAGE = 15

# JWT Configuration (for mini program API)
_JWT_FILE = os.path.join(BASE_DIR, '.jwt_secret')
_JWT_ENV = os.environ.get('JWT_SECRET_KEY', '').strip()
if _JWT_ENV:
    JWT_SECRET_KEY = _JWT_ENV
elif os.path.exists(_JWT_FILE):
    with open(_JWT_FILE, 'r') as f:
        JWT_SECRET_KEY = f.read().strip()
else:
    JWT_SECRET_KEY = secrets.token_hex(32)
    with open(_JWT_FILE, 'w') as f:
        f.write(JWT_SECRET_KEY)
JWT_EXPIRATION_HOURS = 72  # Token valid for 3 days

# Server base URL for constructing absolute URLs (image serving, etc.)
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
