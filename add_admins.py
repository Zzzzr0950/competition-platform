"""添加5个管理员账号"""
import sqlite3, os
from auth_utils import hash_password

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'platform.db')

admins = [
    ('admin2', '管理员2', 'Jxcg@2026#Op2'),
    ('admin3', '管理员3', 'Kjcx@2026#Mn3'),
    ('admin4', '管理员4', 'Xssb@2026#Qw4'),
    ('admin5', '管理员5', 'Ydjy@2026#Zx5'),
    ('admin6', '管理员6', 'Glpt@2026#Lk6'),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for sid, name, pwd in admins:
    existing = cursor.execute("SELECT id FROM users WHERE student_id = ?", [sid]).fetchone()
    if existing:
        print(f'[跳过] {sid} 已存在')
        continue
    cursor.execute(
        "INSERT INTO users (student_id, name, class_name, password_hash, role) VALUES (?, ?, ?, ?, ?)",
        (sid, name, '计算机科学与技术学院', hash_password(pwd), 'admin')
    )
    print(f'[创建] {sid} / {pwd} — {name}')

conn.commit()
conn.close()
print('完成！')
