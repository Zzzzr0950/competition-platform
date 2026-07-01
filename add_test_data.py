"""Add test data for user 2407014310."""
import sqlite3, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import get_db, execute_db
from auth_utils import hash_password

conn = get_db()

# Check if user exists
user = conn.execute("SELECT id FROM users WHERE student_id = '2407014310'").fetchone()
if not user:
    execute_db("""INSERT INTO users (student_id, name, class_name, major, password_hash, phone, role)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ['2407014310', '张紫蓉', '24070143', '计算机科学与技术', hash_password('123456'), '13812345678', 'student'])
    user = conn.execute("SELECT id FROM users WHERE student_id = '2407014310'").fetchone()
    print('用户已创建: 2407014310 / 123456')
else:
    print('用户已存在')

uid = user['id']
now = '2026-07-01 11:25:00'

# Remove old submissions for this user
conn.execute("DELETE FROM submissions WHERE user_id = ?", [uid])

# Add 4 submissions
data = [
    (uid, 52, '二等奖', '国家级', 8, 'NUC_CS', '2407014310 张紫蓉, 2407014311 李四', 1, '2026-05-20'),
    (uid, 54, '三等奖', '国家级', 8, '', '2407014312 王五', 1, '2026-06-10'),
    (uid, 25, '一等奖', '省级', 8, '创意先锋', '2407014310 张紫蓉, 2407014313 赵六', 1, '2026-04-15'),
    (uid, 23, '二等奖', '省级', 0, '', '', 0, '2026-03-22'),
]

for s in data:
    conn.execute("""
        INSERT INTO submissions (user_id, catalog_id, award_level, award_tier, credits,
            team_name, team_members, is_leader, award_date, status, reviewed_by, reviewed_at, created_at)
        VALUES (?,?,?,?,?,?,?,?,?, 'approved', 1, ?, ?)""",
        list(s) + [now, now])
    print(f'已添加: [{s[3]}] {s[4]}学分')

conn.commit()
conn.close()
print('\n完成! 4条申报 + 24学分')
