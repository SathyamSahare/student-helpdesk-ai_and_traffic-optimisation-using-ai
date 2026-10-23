from datetime import datetime, timedelta
import csv
import random

random.seed(7)
output = "traffic_history_demo.csv"
start = datetime(2026, 1, 1, 0, 0)
lanes = ["North", "South"]
rows = []

for i in range(14 * 24 * 4):  # 14 days, 15-minute intervals
    ts = start + timedelta(minutes=15 * i)
    hour = ts.hour
    rush = 1.8 if 7 <= hour <= 9 or 16 <= hour <= 19 else 1.0
    for lane in lanes:
        lane_factor = 1.0 if lane == "North" else 0.8
        count = max(0, int(random.gauss(7 * rush * lane_factor, 2.2)))
        rows.append([ts.isoformat(timespec="minutes"), lane, count])

with open(output, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "lane", "vehicle_count"])
    writer.writerows(rows)

print(f"Created {output} with synthetic sample values.")
print("Replace this demo file with real counts before reporting any model accuracy.")
