import random
import statistics

SEED = 12
SIM_SECONDS = 3600
LANES = ["North", "South", "East", "West"]
MIN_GREEN = 10
MAX_GREEN = 45
CLEARANCE_SECONDS = 3  # simplified yellow/all-red clearance period

def arrivals_per_second(lane, t):
    base = {"North": 0.18, "South": 0.14, "East": 0.12, "West": 0.10}[lane]
    rush = 1.7 if 900 < t < 2700 else 1.0
    return base * rush

def run_simulation(adaptive, seed):
    rng = random.Random(seed)
    queues = {lane: [] for lane in LANES}  # arrival times
    waits = []
    green_index = 0
    green_elapsed = 0
    green_duration = 25
    t = 0

    while t < SIM_SECONDS:
        step = 1
        for lane in LANES:
            if rng.random() < arrivals_per_second(lane, t):
                queues[lane].append(t)

        current_lane = LANES[green_index]
        if queues[current_lane]:
            arrival_time = queues[current_lane].pop(0)
            waits.append(t - arrival_time)

        green_elapsed += 1
        t += step

        if adaptive:
            queue_len = len(queues[current_lane])
            desired = max(MIN_GREEN, min(MAX_GREEN, MIN_GREEN + queue_len * 2))
            should_switch = green_elapsed >= desired
        else:
            should_switch = green_elapsed >= green_duration

        if should_switch:
            for _ in range(CLEARANCE_SECONDS):
                for lane in LANES:
                    if rng.random() < arrivals_per_second(lane, t):
                        queues[lane].append(t)
                t += 1
            green_index = (green_index + 1) % len(LANES)
            green_elapsed = 0
            green_duration = 25

    for lane in LANES:
        waits.extend(SIM_SECONDS - a for a in queues[lane])
    avg_wait = statistics.mean(waits) if waits else 0.0
    return avg_wait, len(waits), {lane: len(queues[lane]) for lane in LANES}

def main():
    seeds = range(SEED, SEED + 10)
    fixed_runs = [run_simulation(False, s) for s in seeds]
    adaptive_runs = [run_simulation(True, s) for s in seeds]
    fixed = statistics.mean(r[0] for r in fixed_runs)
    adaptive = statistics.mean(r[0] for r in adaptive_runs)
    fixed_served = round(statistics.mean(r[1] for r in fixed_runs))
    adaptive_served = round(statistics.mean(r[1] for r in adaptive_runs))
    fixed_queues, adaptive_queues = fixed_runs[0][2], adaptive_runs[0][2]
    print("Averages over 10 random seeds (queues shown for the first seed).")
    print("EDUCATIONAL TOY SIMULATION — synthetic traffic, not real-world evidence")
    print(f"Fixed timing average waiting time:    {fixed:.2f} seconds")
    print(f"Adaptive timing average waiting time: {adaptive:.2f} seconds")
    if fixed > 0:
        change = (fixed - adaptive) / fixed * 100
        print(f"Change in average wait: {change:.1f}% (positive means lower wait in this toy run)")
    print(f"Vehicles served — fixed/adaptive: {fixed_served}/{adaptive_served}")
    print("Remaining queues — fixed:", fixed_queues)
    print("Remaining queues — adaptive:", adaptive_queues)
    print("For a defensible result, use repeated runs and a calibrated simulator such as SUMO.")

if __name__ == "__main__":
    main()
