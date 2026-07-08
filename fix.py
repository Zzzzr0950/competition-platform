from models import query_db, execute_db
from auth_utils import hash_password

execute_db("DELETE FROM users WHERE role='student' AND (class_name LIKE 'B%' OR class_name LIKE 'Y%')")
execute_db("DELETE FROM users WHERE role='student' AND class_name LIKE '22%'")

h = hash_password('123456')
execute_db("UPDATE users SET password_hash = ?, must_change_password = 1 WHERE role = 'student'", [h])

t = query_db("SELECT COUNT(*) as c FROM users WHERE role='student'", one=True)['c']
print('学生总数:', t)
