"""Fixed-time vs adaptive signal control in SUMO (via TraCI).
Usage: python run_sumo.py --seeds 5
Needs: pip install eclipse-sumo traci  (or an installed SUMO with SUMO_HOME set)
Software simulation only. Never connect to real signals.
"""
import argparse, os, statistics, subprocess, sys
import xml.etree.ElementTree as ET

try:
    import sumo
    os.environ.setdefault("SUMO_HOME", sumo.SUMO_HOME)
except ImportError:
    pass
if "SUMO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
    os.environ["PATH"] = os.path.join(os.environ["SUMO_HOME"], "bin") + os.pathsep + os.environ["PATH"]
import traci

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_GREEN, MAX_GREEN, SIM_END = 10, 45, 3600
GREEN_PHASES = {0: ["N_in_0", "S_in_0"], 2: ["E_in_0", "W_in_0"]}  # phase index -> lanes served


def queue(lanes):
    return sum(traci.lane.getLastStepHaltingNumber(l) for l in lanes)


def run(adaptive, seed):
    subprocess.run([sys.executable, os.path.join(HERE, "gen_routes.py"), str(seed)], cwd=HERE, check=True)
    tripinfo = os.path.join(HERE, f"tripinfo_{'adaptive' if adaptive else 'fixed'}_{seed}.xml")
    traci.start(["sumo", "-n", os.path.join(HERE, "net.net.xml"),
                 "-r", os.path.join(HERE, "routes.rou.xml"),
                 "--seed", str(seed), "--end", str(SIM_END),
                 "--tripinfo-output", tripinfo, "--no-step-log", "true",
                 "--no-warnings", "true",
                 "--device.emissions.probability", "1"])
    green_started, last_phase = 0, None
    all_lanes = [l for ls in GREEN_PHASES.values() for l in ls]
    queue_sum, queue_max, steps = 0, 0, 0
    while traci.simulation.getTime() < SIM_END:
        traci.simulationStep()
        q = queue(all_lanes)                      # vehicles stopped at the junction now
        queue_sum, queue_max, steps = queue_sum + q, max(queue_max, q), steps + 1
        if not adaptive:
            continue
        t = traci.simulation.getTime()
        phase = traci.trafficlight.getPhase("C")
        prev, last_phase = last_phase, phase
        if phase in GREEN_PHASES:
            if phase != prev:   # a new green just started: hold it, we decide when it ends
                traci.trafficlight.setPhaseDuration("C", 1000)
                green_started = t
            elapsed = t - green_started
            other = GREEN_PHASES[2 if phase == 0 else 0]
            cur_q, oth_q = queue(GREEN_PHASES[phase]), queue(other)
            if elapsed >= MAX_GREEN and oth_q > 0:
                switch = True
            elif elapsed >= MIN_GREEN and oth_q > 0 and (cur_q == 0 or oth_q > 2 * cur_q):
                switch = True
            else:
                switch = False
            if switch:
                traci.trafficlight.setPhase("C", phase + 1)   # yellow, then auto-advances
    traci.close()
    trips = ET.parse(tripinfo).getroot().findall("tripinfo")
    wait = [float(x.get("waitingTime")) for x in trips]
    travel = [float(x.get("duration")) for x in trips]
    co2 = sum(float(e.get("CO2_abs")) for t in trips for e in t.findall("emissions")) / 1e6  # mg -> kg
    return (statistics.mean(wait), statistics.mean(travel), len(trips),
            queue_sum / max(1, steps), queue_max, co2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    a = ap.parse_args()
    res = {"fixed": [], "adaptive": []}
    for seed in range(1, a.seeds + 1):
        for mode in res:
            r = run(mode == "adaptive", seed)
            res[mode].append(r)
            print(f"seed {seed} {mode:8s} wait={r[0]:6.1f}s travel={r[1]:6.1f}s trips={r[2]} "
                  f"avgQueue={r[3]:.1f} maxQueue={r[4]} CO2={r[5]:.1f}kg")
    print("\nMean over seeds:")
    for mode, r in res.items():
        print(f"{mode:8s} wait={statistics.mean(x[0] for x in r):.1f}s "
              f"travel={statistics.mean(x[1] for x in r):.1f}s trips={statistics.mean(x[2] for x in r):.0f} "
              f"avgQueue={statistics.mean(x[3] for x in r):.1f} "
              f"maxQueue={statistics.mean(x[4] for x in r):.0f} "
              f"CO2={statistics.mean(x[5] for x in r):.0f}kg")


if __name__ == "__main__":
    main()
