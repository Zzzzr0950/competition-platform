"""Remove spaces before Chinese closing quotes in competition names."""
import sqlite3

conn = sqlite3.connect(r'D:\competition-platform\database\platform.db')
conn.row_factory = sqlite3.Row

# Find names with Chinese quotes
rows = conn.execute("SELECT id, name FROM competition_catalog WHERE name LIKE '%“%' OR name LIKE '%”%'").fetchall()

print(f'Entries with Chinese quotes: {len(rows)}')
fixed = 0
for r in rows:
    old = r['name']
    # Remove space before opening quote
    new = old.replace(' “', '“')
    # Remove space before closing quote
    new = new.replace(' ”', '”')
    if new != old:
        conn.execute("UPDATE competition_catalog SET name = ? WHERE id = ?", [new, r['id']])
        fixed += 1
        print(f'Fixed #{r["id"]}: [{old[:40]}] -> [{new[:40]}]')

conn.commit()
print(f'\nFixed {fixed} entries')
conn.close()
