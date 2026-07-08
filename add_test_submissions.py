"""为 2407014310 添加全部7条测试申报"""
from models import query_db, execute_db

uid = query_db("SELECT id FROM users WHERE student_id = '2407014310'", one=True)
if not uid:
    print('用户不存在')
    exit()
uid = uid['id']

# 先清空旧数据
execute_db("DELETE FROM submission_logs WHERE submission_id IN (SELECT id FROM submissions WHERE user_id = ?)", [uid])
execute_db("DELETE FROM submissions WHERE user_id = ?", [uid])
print('已清除旧数据')

# 7条申报
data = [
    # (catalog_id, award_level, award_tier, credits, team_name, team_members, is_leader, award_date, cert, status, reviewed_by)
    (52, '二等奖', '国家级', 8, 'NUC_CS', '2407014310 张紫蓉, 2407014311 李四', 1, '2026-05-20', 'certificates/0d9500d95732.jpg', 'approved', 1),
    (54, '三等奖', '国家级', 8, '', '2407014312 王五', 1, '2026-06-10', 'certificates/10ad949f808d.jpg', 'approved', 1),
    (25, '一等奖', '省级', 8, '创意先锋', '2407014310 张紫蓉, 2407014313 赵六', 1, '2026-04-15', 'certificates/a6a533595307.jpg', 'approved', 1),
    (23, '三等奖', '校级', 0, '', '', 1, '2026-03-01', '', 'approved', 1),
    (1, '一等奖', '国家级', 8, 'ACM-ICPC校队', '队友A、队友B', 1, '2026-06-15', '', 'approved', 1),
    (2, '二等奖', '省级', 5, '', '', 1, '2026-05-20', '', 'approved', 1),
    (3, '三等奖', '校级', 3, '创新项目组', '队友C', 0, '2026-04-10', '', 'pending', None),
]

for cid, award, tier, credits, team, members, leader, date, cert, status, reviewer in data:
    sid = execute_db(
        "INSERT INTO submissions (user_id, catalog_id, award_level, award_tier, credits, team_name, team_members, is_leader, award_date, certificate_image, status, reviewed_by, reviewed_at, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'), datetime('now','localtime'))",
        [uid, cid, award, tier, credits, team, members, leader, date, cert, status, reviewer]
    )
    print(f'  #{sid}: {status}')

t = query_db("SELECT COUNT(*) as c FROM submissions WHERE user_id = ?", [uid], one=True)['c']
print(f'共 {t} 条申报')
