"""Student-facing blueprint: dashboard, submission CRUD, catalog API."""

import os
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, jsonify, current_app)
from models import query_db, execute_db
from auth_utils import login_required, get_current_user
from upload import save_upload, save_uploads, parse_certificate_images
from flask import send_from_directory
from config import UPLOAD_FOLDER, THUMBNAIL_FOLDER

student_bp = Blueprint('student', __name__)


@student_bp.route('/')
@login_required
def dashboard():
    """Student dashboard with stats overview."""
    user = get_current_user()
    if user['role'] == 'admin':
        from flask import redirect as rd
        from admin import admin_bp
        return rd(url_for('admin.dashboard'))

    # Get total credits (approved only, best per competition)
    from credit_calculator import get_student_total_credits
    total_credits, credit_details = get_student_total_credits(user['id'])

    # Get submission counts
    total = query_db(
        "SELECT COUNT(*) as c FROM submissions WHERE user_id = ?",
        [user['id']], one=True
    )['c']
    pending = query_db(
        "SELECT COUNT(*) as c FROM submissions WHERE user_id = ? AND status = 'pending'",
        [user['id']], one=True
    )['c']
    approved = query_db(
        "SELECT COUNT(*) as c FROM submissions WHERE user_id = ? AND status = 'approved'",
        [user['id']], one=True
    )['c']
    rejected = query_db(
        "SELECT COUNT(*) as c FROM submissions WHERE user_id = ? AND status = 'rejected'",
        [user['id']], one=True
    )['c']

    # Recent submissions (last 20)
    recent = query_db("""
        SELECT s.*, c.name as competition_name, c.level as competition_level
        FROM submissions s
        JOIN competition_catalog c ON s.catalog_id = c.id
        WHERE s.user_id = ?
        ORDER BY s.created_at DESC
        LIMIT 20
    """, [user['id']])

    return render_template('student/dashboard.html',
                          user=user, total=total, pending=pending,
                          approved=approved, rejected=rejected, recent=recent,
                          total_credits=total_credits)


@student_bp.route('/submit')
@login_required
def submit():
    """Render the award submission form."""
    # Get active competition catalog for dropdown
    catalog = query_db("""
        SELECT * FROM competition_catalog
        WHERE is_active = 1 AND year = 2026
        ORDER BY sort_order
    """)
    return render_template('student/submit.html', catalog=catalog)


@student_bp.route('/api/submissions', methods=['POST'])
@login_required
def create_submission():
    """Create a new submission via multipart form."""
    user = get_current_user()

    # Parse form data
    catalog_id = request.form.get('catalog_id', '').strip()
    award_level = request.form.get('award_level', '').strip()
    award_tier = request.form.get('award_tier', '').strip()
    award_date = request.form.get('award_date', '').strip()
    team_name = request.form.get('team_name', '').strip()
    team_members = request.form.get('team_members', '').strip()
    is_leader = 1 if request.form.get('is_leader') else 0

    # Validate required fields
    errors = []
    if not catalog_id:
        errors.append('请选择竞赛名称')

    # Validate catalog entry exists and is active (2026)
    catalog_entry = query_db(
        "SELECT * FROM competition_catalog WHERE id = ? AND is_active = 1 AND year = 2026",
        [catalog_id], one=True
    )
    if not catalog_entry:
        errors.append('所选竞赛不在2026年竞赛目录中，请重新选择')

    if not award_level:
        errors.append('请输入获奖等级')
    if not award_tier:
        errors.append('请选择获奖层次')
    if not award_date:
        errors.append('请选择获奖日期')

    # Certificate is mandatory
    files = request.files.getlist('certificate')
    valid_files = [f for f in files if f and f.filename]
    if not valid_files:
        errors.append('请上传获奖证书等证明材料')

    # Calculate credits preview
    from credit_calculator import calculate_credits
    preview_credits = calculate_credits(
        catalog_entry['level'], award_tier, award_level, is_leader
    )

    if errors:
        return jsonify({'error': '; '.join(errors)}), 400

    # Handle file upload (already validated — at least one file exists)
    try:
        certificate_path = save_uploads(valid_files)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    try:
        submission_id = execute_db(
            """INSERT INTO submissions
               (user_id, catalog_id, award_level, award_tier, credits, team_name, team_members,
                is_leader, award_date, certificate_image)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [user['id'], int(catalog_id), award_level, award_tier, preview_credits,
             team_name, team_members, is_leader, award_date, certificate_path]
        )

        # Log the creation
        execute_db(
            """INSERT INTO submission_logs (submission_id, action, new_status, performed_by)
               VALUES (?, 'created', 'pending', ?)""",
            [submission_id, user['id']]
        )

        return jsonify({'success': True, 'id': submission_id,
                       'message': '申报提交成功！请等待管理员审核'})
    except Exception as e:
        return jsonify({'error': f'提交失败: {str(e)}'}), 500


@student_bp.route('/my-submissions')
@login_required
def my_submissions():
    """View own submissions with optional status filter."""
    user = get_current_user()
    status_filter = request.args.get('status', '').strip()

    query = """
        SELECT s.*, c.name as competition_name, c.level as competition_level,
               c.short_name as competition_short
        FROM submissions s
        JOIN competition_catalog c ON s.catalog_id = c.id
        WHERE s.user_id = ?
    """
    params = [user['id']]

    if status_filter and status_filter in ('pending', 'approved', 'rejected'):
        query += " AND s.status = ?"
        params.append(status_filter)

    query += " ORDER BY s.created_at DESC"

    submissions = query_db(query, params)

    return render_template('student/my_submissions.html',
                          submissions=submissions, current_filter=status_filter)


@student_bp.route('/api/submissions/<int:sid>')
@login_required
def get_submission(sid):
    """Get single submission detail (owner or admin)."""
    user = get_current_user()

    sub = query_db("""
        SELECT s.*, c.name as competition_name, c.level as competition_level,
               c.short_name as competition_short, c.category as competition_category
        FROM submissions s
        JOIN competition_catalog c ON s.catalog_id = c.id
        WHERE s.id = ?
    """, [sid], one=True)

    if not sub:
        return jsonify({'error': '申报记录不存在'}), 404

    if sub['user_id'] != user['id'] and user['role'] != 'admin':
        return jsonify({'error': '无权查看此申报记录'}), 403

    # Get reviewer info if reviewed
    reviewer = None
    if sub['reviewed_by']:
        reviewer = query_db(
            "SELECT name FROM users WHERE id = ?", [sub['reviewed_by']], one=True
        )

    return jsonify({
        'id': sub['id'],
        'competition_name': sub['competition_name'],
        'competition_level': sub['competition_level'],
        'competition_category': sub['competition_category'],
        'award_level': sub['award_level'],
        'award_tier': sub['award_tier'] or '国家级',
        'credits': sub['credits'] or 0,
        'award_date': sub['award_date'],
        'team_name': sub['team_name'],
        'team_members': sub['team_members'],
        'is_leader': sub['is_leader'],
        'certificate_image': sub['certificate_image'],
        'status': sub['status'],
        'review_comment': sub['review_comment'],
        'reviewer_name': reviewer['name'] if reviewer else None,
        'reviewed_at': sub['reviewed_at'],
        'created_at': sub['created_at']
    })


@student_bp.route('/api/submissions/<int:sid>', methods=['PUT'])
@login_required
def update_submission(sid):
    """Edit a pending submission (before review)."""
    user = get_current_user()

    sub = query_db("SELECT * FROM submissions WHERE id = ?", [sid], one=True)
    if not sub:
        return jsonify({'error': '申报记录不存在'}), 404
    if sub['user_id'] != user['id']:
        return jsonify({'error': '无权修改此申报记录'}), 403
    if sub['status'] != 'pending':
        return jsonify({'error': '只能修改待审核状态的申报'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400

    updates = []
    params = []
    allowed_fields = ['award_level', 'award_date', 'team_name', 'team_members', 'is_leader']

    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])

    if not updates:
        return jsonify({'error': '没有需要更新的字段'}), 400

    updates.append("updated_at = datetime('now','localtime')")
    params.append(sid)

    execute_db(f"UPDATE submissions SET {', '.join(updates)} WHERE id = ?", params)

    # Log update
    execute_db(
        "INSERT INTO submission_logs (submission_id, action, new_status, performed_by) VALUES (?, 'updated', 'pending', ?)",
        [sid, user['id']]
    )

    return jsonify({'success': True, 'message': '申报已更新'})


@student_bp.route('/api/submissions/<int:sid>', methods=['DELETE'])
@login_required
def delete_submission(sid):
    """Delete a pending submission."""
    user = get_current_user()

    sub = query_db("SELECT * FROM submissions WHERE id = ?", [sid], one=True)
    if not sub:
        return jsonify({'error': '申报记录不存在'}), 404
    if sub['user_id'] != user['id']:
        return jsonify({'error': '无权删除此申报记录'}), 403
    if sub['status'] != 'pending':
        return jsonify({'error': '只能删除待审核状态的申报'}), 400

    execute_db("DELETE FROM submission_logs WHERE submission_id = ?", [sid])
    execute_db("DELETE FROM submissions WHERE id = ?", [sid])

    return jsonify({'success': True, 'message': '申报已删除'})


@student_bp.route('/api/catalog')
@login_required
def get_catalog():
    """Get active competition catalog entries for dropdowns."""
    search = request.args.get('search', '').strip()
    level = request.args.get('level', '').strip()

    query = "SELECT * FROM competition_catalog WHERE is_active = 1 AND year = 2026"
    params = []

    if search:
        query += " AND (name LIKE ? OR short_name LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    if level:
        query += " AND level = ?"
        params.append(level)

    query += " ORDER BY sort_order"

    items = query_db(query, params)
    return jsonify([{
        'id': item['id'],
        'name': item['name'],
        'short_name': item['short_name'],
        'category': item['category'],
        'level': item['level'],
        'organizer': item['organizer'],
        'is_key_competition': item['is_key_competition']
    } for item in items])


@student_bp.route('/submission/<int:sid>')
@login_required
def submission_detail(sid):
    """Render single submission detail page."""
    user = get_current_user()
    sub = query_db("""
        SELECT s.*, c.name as competition_name, c.level as competition_level,
               c.short_name as competition_short, c.category as competition_category,
               c.is_key_competition, c.organizer as competition_organizer
        FROM submissions s
        JOIN competition_catalog c ON s.catalog_id = c.id
        WHERE s.id = ?
    """, [sid], one=True)

    if not sub:
        flash('申报记录不存在', 'error')
        return redirect(url_for('student.my_submissions'))

    if sub['user_id'] != user['id'] and user['role'] != 'admin':
        flash('无权查看此申报记录', 'error')
        return redirect(url_for('student.my_submissions'))

    # Get reviewer info
    reviewer = None
    if sub['reviewed_by']:
        reviewer = query_db("SELECT name FROM users WHERE id = ?", [sub['reviewed_by']], one=True)

    status_map = {'pending': '审核中', 'approved': '已通过', 'rejected': '已驳回'}
    cert_images = parse_certificate_images(sub['certificate_image'] or '')

    return render_template('student/submission_detail.html',
                          sub=sub, reviewer=reviewer, status_map=status_map,
                          cert_images=cert_images)


@student_bp.route('/uploads/<path:filename>')
@login_required
def serve_upload(filename):
    """Serve uploaded files (protected - requires login)."""
    # Determine which folder
    if filename.startswith('thumbnails/'):
        folder = THUMBNAIL_FOLDER
        filename = filename.replace('thumbnails/', '', 1)
    elif filename.startswith('certificates/'):
        folder = UPLOAD_FOLDER
        filename = filename.replace('certificates/', '', 1)
    else:
        folder = UPLOAD_FOLDER
    return send_from_directory(folder, filename)
