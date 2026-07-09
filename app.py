"""竞享成果——学生竞赛获奖申报平台
Flask application entry point.
"""

from flask import Flask
from config import SECRET_KEY, DATABASE_PATH, UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from models import init_db


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configuration
    app.secret_key = SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Initialize database
    init_db()

    # Seed initial data (idempotent)
    from seed_data import seed_if_empty
    with app.app_context():
        seed_if_empty()

    # Register blueprints
    from auth import auth_bp
    from student import student_bp
    from admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # Register mini program API blueprint (JWT-based)
    from api_bp import api_bp
    app.register_blueprint(api_bp)

    # 禁止浏览器缓存，防止手机退出后显示混乱
    @app.after_request
    def no_cache(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('error.html', code=404, message='页面未找到'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('error.html', code=500, message='服务器内部错误'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 50)
    print("  竞享成果——学生竞赛获奖申报平台")
    print("  中北大学计算机科学与技术学院")
    print("=" * 50)
    print(f"  访问地址: http://localhost:5000")
    print(f"  默认管理员: admin / admin123")
    print("=" * 50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
