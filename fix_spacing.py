"""Clean all spacing issues from seed_data, JSON files, and database.
Fixes:
  1. Double Chinese quotes "" -> "  and  "" -> "
  2. Spaces around middle dot ' · ' -> '·'
  3. Space before right Chinese quote ' "' -> '"'
"""
import re
import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'platform.db')

def clean_name(text):
    """Remove unwanted spaces and fix doubled Chinese quotes."""
    # Fix double Chinese quotes
    t = text.replace('““', '“')  # "" -> "
    t = t.replace('””', '”')     # "" -> "
    # Remove space before Chinese right quote
    t = re.sub(r' ”', '”', t)
    # Remove spaces around middle dot
    t = re.sub(r' · ', '·', t)
    return t

# ===== 1. Fix seed_data.py =====
with open('seed_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Apply clean_name to each line inside string literals
# Simpler: just do the replacements globally in the file
fixed = content
fixed = fixed.replace('““', '“')  # "" -> "
fixed = fixed.replace('””', '”')  # "" -> "
fixed = re.sub(r' ”', '”', fixed)      # " -> "
fixed = re.sub(r' · ', '·', fixed)      # · space -> ·
fixed = re.sub(r'· ', '·', fixed)        # · space -> ·
fixed = re.sub(r' ·', '·', fixed)        # space· -> ·

with open('seed_data.py', 'w', encoding='utf-8') as f:
    f.write(fixed)

# Show changes
old_lines = content.split('\n')
new_lines = fixed.split('\n')
changes = 0
for i, (o, n) in enumerate(zip(old_lines, new_lines)):
    if o != n:
        changes += 1
        print(f'[seed_data.py L{i+1}] changed')
print(f'seed_data.py: {changes} lines changed')

# ===== 2. Fix parsed_catalog.json =====
with open('parsed_catalog.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

pc = 0
for item in data:
    for key in ('name', 'short_name'):
        if key in item:
            old = item[key]
            new = clean_name(old)
            if old != new:
                item[key] = new
                pc += 1
                print(f'[parsed_catalog #{item.get("sort_order","?")}] {old[:60]} -> {new[:60]}')

with open('parsed_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'parsed_catalog.json: {pc} fields fixed')

# ===== 3. Fix catalog_raw.json =====
with open('catalog_raw.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

rc = 0
for row in raw:
    if len(row) >= 2:
        old = row[1]
        new = clean_name(old)
        if old != new:
            row[1] = new
            rc += 1
            print(f'[catalog_raw] {old[:60]} -> {new[:60]}')

with open('catalog_raw.json', 'w', encoding='utf-8') as f:
    json.dump(raw, f, ensure_ascii=False, indent=2)
print(f'catalog_raw.json: {rc} fields fixed')

# ===== 4. Fix database =====
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT id, name, short_name FROM competition_catalog')
rows = cursor.fetchall()

dc = 0
for row in rows:
    id_, name, short = row
    new_name = clean_name(name)
    new_short = clean_name(short) if short else ''
    if new_name != name or new_short != short:
        cursor.execute('UPDATE competition_catalog SET name=?, short_name=? WHERE id=?',
                       (new_name, new_short, id_))
        dc += 1
        print(f'[DB #{id_}] {name[:50]} -> {new_name[:50]}')

conn.commit()
conn.close()
print(f'database: {dc} entries fixed')
print('\nAll done!')
