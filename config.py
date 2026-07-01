"""Application configuration constants."""

import os
import secrets

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask secret key for session signing (use env var in production)
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))

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
