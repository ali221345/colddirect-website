import csv
clicks_total = 0
impressions_total = 0
position_total = 0
count = 0

with open('gsc_report.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['section'] in ['top_queries', 'top_pages']:
            clicks_total += int(row['clicks'])
            impressions_total += int(row['impressions'])
            position_total += float(row['position'])
            count += 1

avg_position = position_total / count if count > 0 else 0
avg_ctr = clicks_total / impressions_total * 100 if impressions_total > 0 else 0

print(f'Site Totals (Aug 30 - Sep 26):')
print(f'  Total clicks: {clicks_total}')
print(f'  Total impressions: {impressions_total}')
print(f'  Avg CTR: {avg_ctr:.2f}%')
print(f'  Avg position: {avg_position:.2f}')
