"""批量导入学生账号
使用方法：
  1. 准备 students.csv（UTF-8 编码），列：学号,姓名,班级,专业
  2. 运行：python import_students.py students.csv

CSV 示例：
学号,姓名,班级,专业
2407014301,张三,24070143,计算机科学与技术
2407014302,李四,24070143,计算机科学与技术
"""
import csv
import os
import sys
from auth_utils import hash_password

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'platform.db')


def import_students(csv_path, default_password=None):
    """从 CSV 导入学生账号。默认密码为学号后6位。"""
    import sqlite3

    if not os.path.exists(csv_path):
        print(f'[错误] 文件不存在: {csv_path}')
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    created = 0
    skipped = 0
    errors = []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            student_id = row.get('学号', '').strip()
            name = row.get('姓名', '').strip()
            class_name = row.get('班级', '').strip()
            major = row.get('专业', '').strip()

            if not student_id or not name:
                errors.append(f'第{row_num}行：学号或姓名为空，跳过')
                skipped += 1
                continue

            # 检查是否已存在
            existing = cursor.execute(
                "SELECT id FROM users WHERE student_id = ?", [student_id]
            ).fetchone()
            if existing:
                skipped += 1
                continue

            # 密码：默认学号后6位，也可通过参数指定
            if default_password:
                pwd = default_password
            else:
                pwd = student_id[-6:] if len(student_id) >= 6 else student_id

            try:
                cursor.execute(
                    """INSERT INTO users (student_id, name, class_name, major, password_hash, must_change_password)
                       VALUES (?, ?, ?, ?, ?, 1)""",
                    [student_id, name, class_name, major, hash_password(pwd)]
                )
                created += 1
            except Exception as e:
                errors.append(f'第{row_num}行({student_id}): {e}')
                skipped += 1

    conn.commit()
    conn.close()

    print(f'\n===== 导入完成 =====')
    print(f'新增: {created} 人')
    print(f'跳过（已存在/数据不全）: {skipped} 人')
    if default_password:
        print(f'初始密码: {default_password}')
    else:
        print(f'初始密码: 学号后6位')
    print(f'首次登录会强制要求修改密码')
    if errors:
        print(f'\n异常:')
        for e in errors:
            print(f'  {e}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python import_students.py <csv文件路径> [默认密码]')
        print('示例: python import_students.py students.csv')
        print('      python import_students.py students.csv 123456')
        sys.exit(1)

    pwd = sys.argv[2] if len(sys.argv) > 2 else None
    import_students(sys.argv[1], pwd)
