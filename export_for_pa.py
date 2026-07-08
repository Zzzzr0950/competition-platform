"""Export students to SQL for PythonAnywhere import"""
from models import query_db

rows = query_db("SELECT * FROM users WHERE role='student'")
print(f'Exporting {len(rows)} students...')

with open('students_export.sql', 'w', encoding='utf-8') as f:
    # Clear existing students first
    f.write("DELETE FROM users WHERE role='student';\n\n")
    for r in rows:
        name = (r['name'] or '').replace("'", "''")
        major = (r['major'] or '').replace("'", "''")
        class_name = (r['class_name'] or '').replace("'", "''")
        phone = r['phone'] or ''
        qq = r['qq'] or ''
        created = r['created_at'] or ''
        f.write(f"INSERT INTO users (student_id, name, class_name, major, password_hash, role, phone, qq, is_active, created_at, must_change_password) ")
        f.write(f"VALUES ('{r['student_id']}', '{name}', '{class_name}', '{major}', '{r['password_hash']}', 'student', '{phone}', '{qq}', 1, '{created}', 1);\n")

import os
size = os.path.getsize('students_export.sql')
print(f'Done: students_export.sql ({size:,} bytes)')
