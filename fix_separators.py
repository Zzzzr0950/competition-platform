"""Remove spaces before separators in competition names."""
import sqlite3, re

conn = sqlite3.connect(r'D:\competition-platform\database\platform.db')
conn.row_factory = sqlite3.Row

rows = conn.execute("SELECT id, name FROM competition_catalog").fetchall()

fixed = 0
for r in rows:
    old = r['name']
    # Remove space before Chinese/English colons, dashes, brackets, slashes
    new = re.sub(r'\s+([：:—–\-—（）()/、，,。.《》<>])', r'\1', old)
    if new != old:
        conn.execute("UPDATE competition_catalog SET name = ? WHERE id = ?", [new, r['id']])
        fixed += 1
        print(f'Fixed #{r["id"]}: [{old[:50]}] -> [{new[:50]}]')

conn.commit()
print(f'\nFixed {fixed} entries')
conn.close()
