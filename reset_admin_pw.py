"""重置所有管理员密码为复杂密码"""
import sqlite3, os
from auth_utils import hash_password

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'platform.db')

# 复杂密码：数字+大小写字母的组合
admins = {
    'admin':  'Nuc@2026#Ad1',
    'admin2': 'Jxcg@2026#Op2',
    'admin3': 'Kjcx@2026#Mn3',
    'admin4': 'Xssb@2026#Qw4',
    'admin5': 'Ydjy@2026#Zx5',
    'admin6': 'Glpt@2026#Lk6',
}

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for sid, pwd in admins.items():
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE student_id = ? AND role = 'admin'",
        (hash_password(pwd), sid)
    )
    if cursor.rowcount > 0:
        print(f'[更新] {sid} → {pwd}')
    else:
        print(f'[未找到] {sid}')

conn.commit()
conn.close()
print('完成！请妥善保管新密码。')
