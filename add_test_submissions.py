"""为 2407014310 添加测试申报数据"""
from models import query_db, execute_db
from credit_calculator import calculate_credits

uid = query_db("SELECT id FROM users WHERE student_id = '2407014310'", one=True)
if not uid:
    print('用户不存在')
    exit()
uid = uid['id']

# 取前3个竞赛
comps = query_db("SELECT id, name, level FROM competition_catalog WHERE is_active = 1 ORDER BY sort_order LIMIT 3")

data = [
    (comps[0]['id'], '一等奖', '国家级', '2026-06-15', 'ACM-ICPC校队', '队友A、队友B', 1, 'approved'),
    (comps[1]['id'], '二等奖', '省级', '2026-05-20', '', '', 1, 'approved'),
    (comps[2]['id'], '三等奖', '校级', '2026-04-10', '创新项目组', '队友C', 0, 'pending'),
]

for i, (cid, award, tier, date, team, members, leader, status) in enumerate(data):
    comp_level = comps[i]['level']
    credits = calculate_credits(comp_level, tier, award, leader)
    sid = execute_db(
        "INSERT INTO submissions (user_id, catalog_id, award_level, award_tier, credits, team_name, team_members, is_leader, award_date, status, reviewed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'))",
        [uid, cid, award, tier, credits, team, members, leader, date, status]
    )
    print(f'已添加 #{sid}: {status} ({credits}学分)')

t = query_db("SELECT COUNT(*) as c FROM submissions WHERE user_id = ?", [uid], one=True)['c']
print(f'共 {t} 条申报')
