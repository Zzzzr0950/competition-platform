"""Authentication blueprint: login, register, logout."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import query_db, execute_db
from auth_utils import hash_password, verify_password, login_required, get_current_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication handler."""
    # 已登录用户直接跳转
    if session.get('user_id'):
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        password = request.form.get('password', '')

        if not student_id or not password:
            flash('请输入学号和密码', 'warning')
            return render_template('login.html')

        user = query_db(
            "SELECT * FROM users WHERE student_id = ? AND is_active = 1",
            [student_id], one=True
        )

        if user is None or not verify_password(password, user['password_hash']):
            flash('学号或密码错误', 'error')
            return render_template('login.html')

        # Set session
        session.permanent = True
        session['user_id'] = user['id']
        session['student_id'] = user['student_id']
        session['name'] = user['name']
        session['role'] = user['role']

        # 批量导入的账号首次登录必须修改密码
        if user['must_change_password']:
            flash('请先修改初始密码后再使用系统', 'warning')
            return redirect(url_for('auth.change_password'))

        flash(f'欢迎回来，{user["name"]}！', 'success')

        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page (disabled by default, use batch import)."""
    from config import ALLOW_REGISTRATION
    if not ALLOW_REGISTRATION:
        flash('暂未开放公开注册，请联系管理员', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        name = request.form.get('name', '').strip()
        class_name = request.form.get('class_name', '').strip()
        major = request.form.get('major', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()
        qq = request.form.get('qq', '').strip()
        phone = request.form.get('phone', '').strip()

        # Validation
        errors = []
        if not student_id or len(student_id) < 6:
            errors.append('请输入有效的学号')
        if not name:
            errors.append('请输入姓名')
        if not class_name:
            errors.append('请输入班级')
        if not major:
            errors.append('请输入专业')
        if not phone or len(phone) < 11:
            errors.append('请输入正确的手机号')
        if len(password) < 6:
            errors.append('密码长度不能少于6位')
        if password != password_confirm:
            errors.append('两次输入的密码不一致')

        if errors:
            for e in errors:
                flash(e, 'warning')
            return render_template('register.html')

        # Check if student_id already exists
        existing = query_db(
            "SELECT id FROM users WHERE student_id = ?", [student_id], one=True
        )
        if existing:
            flash('该学号已被注册', 'error')
            return render_template('register.html')

        try:
            execute_db(
                """INSERT INTO users (student_id, name, class_name, major, password_hash, qq, phone)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [student_id, name, class_name, major, hash_password(password), qq, phone]
            )
            flash('注册成功！请登录', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'注册失败: {str(e)}', 'error')

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout and clear session."""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page (also update QQ and phone)."""
    user = get_current_user()

    if request.method == 'POST':
        old_pw = request.form.get('old_password', '').strip()
        new_pw = request.form.get('new_password', '').strip()
        confirm_pw = request.form.get('confirm_password', '').strip()
        qq = request.form.get('qq', '').strip()
        phone = request.form.get('phone', '').strip()

        if not verify_password(old_pw, user['password_hash']):
            flash('原密码错误', 'error')
        elif len(new_pw) < 6:
            flash('新密码长度不能少于6位', 'warning')
        elif new_pw != confirm_pw:
            flash('两次输入的新密码不一致', 'warning')
        elif not phone:
            flash('请输入手机号', 'warning')
        else:
            execute_db(
                "UPDATE users SET password_hash = ?, must_change_password = 0, qq = ?, phone = ? WHERE id = ?",
                [hash_password(new_pw), qq, phone, session['user_id']]
            )
            flash('密码修改成功', 'success')

            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))

    return render_template('change_password.html', user=user)
