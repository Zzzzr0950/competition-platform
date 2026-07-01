"""Fix English double/single quotes in competition names to Chinese double quotes."""
import json, sqlite3, re

# Load parsed JSON
with open(r'D:\competition-platform\parsed_catalog.json', 'r', encoding='utf-8') as f:
    comps = json.load(f)

# Competition names that should have Chinese double quotes around keywords
# Based on standard Chinese competition naming conventions
fixes = {
    "挑战杯": ("“挑战杯”", "挑战杯"),  # "挑战杯"
    "大唐杯": ("“大唐杯”", "大唐杯"),
    "学创杯": ("“学创杯”", "学创杯"),
    "西门子杯": ("“西门子杯”", "西门子杯"),
    "百度之星": ("“百度之星”", "百度之星"),
    "工行杯": ("“工行杯”", "工行杯"),
    "科云杯": ("“科云杯”", "科云杯"),
    "华灿奖": ("“华灿奖”", "华灿奖"),
}

fixed = 0
for c in comps:
    old = c['name']
    new = old
    for keyword, (cn_quoted, _) in fixes.items():
        if keyword in new:
            # Find the keyword in the name and wrap it with Chinese quotes
            # But only if it's not already wrapped
            if '“' + keyword + '”' not in new:
                new = new.replace(keyword, cn_quoted)
    if new != old:
        c['name'] = new
        c['short_name'] = new[:15]
        fixed += 1
        print(f'Fixed: {old[:40]} -> {new[:40]}')

print(f'\nFixed {fixed} competition names')

# Save updated JSON
with open(r'D:\competition-platform\parsed_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(comps, f, ensure_ascii=False, indent=2)

# Now update the database directly
conn = sqlite3.connect(r'D:\competition-platform\database\platform.db')
for c in comps:
    conn.execute("UPDATE competition_catalog SET name = ?, short_name = ? WHERE name LIKE ?",
                 [c['name'], c['short_name'], f'%{c["name"][:20]}%'])
conn.commit()

# Verify
rows = conn.execute("SELECT id, name FROM competition_catalog WHERE name LIKE '%“%'").fetchall()
print(f'\nEntries with Chinese quotes in DB: {len(rows)}')
for r in rows:
    print(f'  #{r[0]}: {r[1][:60]}')
conn.close()
