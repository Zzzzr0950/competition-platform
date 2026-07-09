from models import query_db

# 检查管理员
u = query_db("SELECT id, student_id, name, must_change_password FROM users WHERE student_id = 'admin'", one=True)
if u:
    print('admin:', u['name'])
    print('must_change_password:', u['must_change_password'], type(u['must_change_password']))
else:
    print('admin 账号不存在!')

# 检查学生总数
t = query_db("SELECT COUNT(*) as c FROM users WHERE role='student'", one=True)['c']
print('学生数:', t)

print('done')
