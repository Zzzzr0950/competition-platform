"""一键设置学生账号：导入 + 清理 + 重置密码"""
import os
import sys
from models import query_db, execute_db
from auth_utils import hash_password

EXCEL_FILE = "附件1《计算机科学与技术学院2025年学生名单》.xlsx"

print("===== 步骤1: 导入学生 =====")
if os.path.exists(EXCEL_FILE):
    from import_students import import_students
    import_students(EXCEL_FILE)
else:
    print(f"[跳过] 未找到 {EXCEL_FILE}，如已导入请忽略")

print("\n===== 步骤2: 清理 B/Y 班级 =====")
execute_db("DELETE FROM users WHERE role='student' AND (class_name LIKE 'B%' OR class_name LIKE 'Y%')")
print("B/Y 班级已删除")

print("\n===== 步骤3: 清理 2022 级 =====")
execute_db("DELETE FROM users WHERE role='student' AND class_name LIKE '22%'")
print("2022 级已删除")

print("\n===== 步骤4: 重置密码 =====")
h = hash_password('123456')
execute_db("UPDATE users SET password_hash = ?, must_change_password = 1 WHERE role = 'student'", [h])
print("全部密码: 123456，首次登录强制修改")

print("\n===== 完成 =====")
t = query_db("SELECT COUNT(*) as c FROM users WHERE role='student'", one=True)['c']
print(f"学生总数: {t}")
for pre, label in [('23%','2023级'),('24%','2024级'),('25%','2025级')]:
    n = query_db("SELECT COUNT(*) as c FROM users WHERE role='student' AND class_name LIKE ?", [pre], one=True)['c']
    print(f"  {label}: {n} 人")
