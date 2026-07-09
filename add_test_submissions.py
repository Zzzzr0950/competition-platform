"""为 2407014310 添加2条正确申报+证明图片"""
from models import query_db, execute_db
from credit_calculator import calculate_credits

uid = query_db("SELECT id FROM users WHERE student_id = '2407014310'", one=True)['id']

# 选两个合适的竞赛 + 现有证书图片
data = [
    # (catalog_id, 获奖等级, 获奖层次, 获奖日期, 团队名, 团队成员, 是否队长, 证书图片, 状态)
    (1, '一等奖', '国家级', '2026-06-15', 'NUC_CS', '2407014311 李四', 1, 'certificates/0d9500d95732.jpg', 'approved'),
    (2, '一等奖', '省级', '2026-05-20', '创新先锋', '2407014312 王五', 1, 'certificates/10ad949f808d.jpg', 'approved'),
]

for cid, award, tier, date, team, members, leader, cert, status in data:
    comp = query_db("SELECT name, level FROM competition_catalog WHERE id = ?", [cid], one=True)
    credits = calculate_credits(comp['level'], tier, award, leader)
    sid = execute_db(
        "INSERT INTO submissions (user_id, catalog_id, award_level, award_tier, credits, team_name, team_members, is_leader, award_date, certificate_image, status, reviewed_by, reviewed_at, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, datetime('now','localtime'), datetime('now','localtime'))",
        [uid, cid, award, tier, credits, team, members, leader, date, cert, status]
    )
    print(f'#{sid}: {comp["name"][:25]} | {tier} {award} | {credits}学分 | {status}')

t = query_db("SELECT COUNT(*) as c FROM submissions", one=True)['c']
print(f'共 {t} 条申报')
