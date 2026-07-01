"""Authentication utilities: password hashing and role-based decorators."""

from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    """Hash a password using werkzeug's secure hashing."""
    return generate_password_hash(password, method='scrypt')


def verify_password(password, password_hash):
    """Verify a password against its hash."""
    return check_password_hash(password_hash, password)


def get_current_user():
    """Get the current logged-in user's info from session."""
    from models import query_db
    user_id = session.get('user_id')
    if not user_id:
        return None
    return query_db("SELECT * FROM users WHERE id = ? AND is_active = 1", [user_id], one=True)


def login_required(f):
    """Decorator: requires student or admin login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            flash('请先登录后再访问该页面', 'warning')
            return redirect(url_for('auth.login'))
        # Check user is still active
        user = get_current_user()
        if user is None:
            session.clear()
            flash('账户已被禁用，请联系管理员', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator: requires admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            flash('请先登录后再访问该页面', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('无权访问管理页面', 'error')
            return redirect(url_for('student.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
