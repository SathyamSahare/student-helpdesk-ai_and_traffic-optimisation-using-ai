"""Software-only signal timing recommendation; no physical signal connection."""
from dataclasses import dataclass

@dataclass
class SignalRecommendation:
    lane: str
    green_seconds: int
    reason: str

MIN_GREEN = 10
MAX_GREEN = 45
YELLOW_SECONDS = 3
ALL_RED_SECONDS = 1

def recommend_green(vehicle_count: int, lane: str) -> SignalRecommendation:
    """Map observed queue count to a bounded demo recommendation."""
    count = max(0, int(vehicle_count))
    green = min(MAX_GREEN, max(MIN_GREEN, MIN_GREEN + count * 2))
    return SignalRecommendation(
        lane=lane,
        green_seconds=green,
        reason=f"{count} detected vehicles; demo rule gives {green}s green"
    )

def print_cycle(vehicle_counts):
    """Print recommendations only. Does not switch hardware."""
    for lane, count in vehicle_counts.items():
        rec = recommend_green(count, lane)
        print(f"{rec.lane}: GREEN {rec.green_seconds}s — {rec.reason}")
        print(f"  then YELLOW {YELLOW_SECONDS}s and ALL-RED {ALL_RED_SECONDS}s clearance")

if __name__ == "__main__":
    print_cycle({"North": 18, "South": 5, "East": 11, "West": 2})
