"""学分认定计算模块

根据中北大学学科竞赛学分认定标准，自动计算每项申报的学分。

认定标准：
  一、超级、一级竞赛
    1. 国家级获奖全体成员 / 省级一等奖负责人 → 8学分
    2. 省级一等奖除负责人外其余团队成员 → 4学分

  二、其他竞赛（二级、三级）
    1. 国家级一、二等奖全体成员 / 国家级三等奖团队负责人 → 8学分
    2. 国家级三等奖其余团队成员 / 省级一等奖负责人 → 4学分

  三、通用规则
    1. 竞赛级别依据学校每年发布的学科竞赛目录
    2. 无团队负责人的竞赛，所有队员统一按普通成员标准
    3. 超级竞赛国家级≤15人、省级≤10人；其余竞赛≤5人
    4. 同一学生同一年度同一竞赛，仅按最高奖项核算学分
"""


def extract_award_rank(award_level):
    """从获奖等级文本中提取等级关键词。

    Returns one of: '特等奖', '一等奖', '二等奖', '三等奖', '其他'
    """
    text = award_level.strip()
    for rank in ['特等奖', '一等奖', '二等奖', '三等奖']:
        if rank in text:
            return rank
    return '其他'


def calculate_credits(competition_level, award_tier, award_level, is_leader):
    """计算单项申报的认定学分。

    Args:
        competition_level: 竞赛级别 — '超级', '一级', '二级', '三级'
        award_tier: 获奖层次 — '国家级', '省级'
        award_level: 获奖等级 — 自由文本，如 '一等奖', '金奖' 等
        is_leader: 是否团队负责人 — 1/0 或 True/False

    Returns:
        int: 认定学分 (0, 4, 或 8)
    """
    is_leader = int(is_leader) if is_leader is not None else 1
    rank = extract_award_rank(award_level)
    is_super_or_first = competition_level in ('超级', '一级')

    if is_super_or_first:
        # 一、超级、一级竞赛
        if award_tier == '国家级':
            # 1. 国家级获奖全体成员 → 8学分
            return 8
        elif award_tier == '省级' and rank == '一等奖':
            # 2. 省级一等奖负责人 → 8学分；其余成员 → 4学分
            return 8 if is_leader else 4
        else:
            return 0
    else:
        # 二、其他竞赛（二级、三级）
        if award_tier == '国家级':
            if rank in ('特等奖', '一等奖', '二等奖'):
                # 1. 国家级一、二等奖全体成员 → 8学分
                return 8
            elif rank == '三等奖':
                # 2. 国家级三等奖负责人 → 8学分；其余成员 → 4学分
                return 8 if is_leader else 4
            else:
                return 0
        elif award_tier == '省级' and rank == '一等奖':
            # 3. 省级一等奖负责人 → 4学分
            return 4 if is_leader else 0
        else:
            return 0


def get_student_total_credits(student_id):
    """获取某学生同一竞赛年度内按最高奖项核算后的总学分。

    规则：同一学生同一年度参与同一竞赛，仅按该竞赛内最高奖项核算学分。
    """
    from models import query_db

    # 获取该学生所有已通过的申报
    submissions = query_db("""
        SELECT s.id, s.catalog_id, s.award_level, s.award_tier, s.is_leader, s.credits,
               c.name as competition_name, c.level as competition_level
        FROM submissions s
        JOIN competition_catalog c ON s.catalog_id = c.id
        WHERE s.user_id = ? AND s.status = 'approved'
        ORDER BY s.catalog_id, s.credits DESC
    """, [student_id])

    if not submissions:
        return 0, []

    # 同一竞赛只取最高学分
    best = {}
    details = []
    for s in submissions:
        cid = s['catalog_id']
        if cid not in best or s['credits'] > best[cid]['credits']:
            best[cid] = s

    total = sum(b['credits'] for b in best.values())
    detail_list = list(best.values())

    return total, detail_list


def calculate_student_credits(student_id):
    """重新计算某学生所有已通过申报的学分并更新数据库。"""
    from models import query_db, execute_db

    submissions = query_db("""
        SELECT s.id, s.award_level, s.award_tier, s.is_leader,
               c.level as competition_level
        FROM submissions s
        JOIN competition_catalog c ON s.catalog_id = c.id
        WHERE s.user_id = ? AND s.status = 'approved'
    """, [student_id])

    for s in submissions:
        new_credits = calculate_credits(
            s['competition_level'],
            s['award_tier'] or '国家级',
            s['award_level'],
            s['is_leader']
        )
        if new_credits != (s['credits'] or 0):
            execute_db("UPDATE submissions SET credits = ? WHERE id = ?",
                       [new_credits, s['id']])

    total, _ = get_student_total_credits(student_id)
    return total
