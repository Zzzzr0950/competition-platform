"""一键修复第16项竞赛的名称、简称、主办单位。
在 PythonAnywhere 的 Bash console 中运行：
    cd ~/mysite
    python fix_competition_16.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'platform.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 查看当前数据
cursor.execute('SELECT id, name, short_name, organizer FROM competition_catalog WHERE id = 16')
old = cursor.fetchone()
print(f'[旧数据] id={old[0]}, name={old[1]}, short_name={old[2]}, organizer={old[3]}')

# 更新为正确值
cursor.execute('''
    UPDATE competition_catalog
    SET name = ?,
        short_name = ?,
        organizer = ?
    WHERE id = 16
''', (
    '全国大学生基础医学创新研究暨实验设计论坛（大赛）',
    '全国大学生基础医学创新研究暨实',
    '信息与通信工程学院'
))
conn.commit()

# 验证
cursor.execute('SELECT id, name, short_name, organizer FROM competition_catalog WHERE id = 16')
new = cursor.fetchone()
print(f'[新数据] id={new[0]}, name={new[1]}, short_name={new[2]}, organizer={new[3]}')
print('修复完成！')
conn.close()
