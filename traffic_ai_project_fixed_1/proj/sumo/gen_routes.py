"""Generate demand for the 4-way junction. Usage: python gen_routes.py SEED"""
import sys
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
# vehicles/hour; rush-like increase between 900s and 2700s
base = {"N": 500, "S": 400, "E": 350, "W": 300}
opp = {"N": "S", "S": "N", "E": "W", "W": "E"}
lines = ['<routes>', '<vType id="car" accel="2.6" decel="4.5" length="5" maxSpeed="13.9"/>']
for d in base:
    lines.append(f'<route id="r_{d}" edges="{d}_in {opp[d]}_out"/>')
for d, v in base.items():
    lines.append(f'<flow id="f_{d}_a" type="car" route="r_{d}" begin="0" end="900" vehsPerHour="{v}" departLane="best"/>')
    lines.append(f'<flow id="f_{d}_b" type="car" route="r_{d}" begin="900" end="2700" vehsPerHour="{int(v*1.7)}" departLane="best"/>')
    lines.append(f'<flow id="f_{d}_c" type="car" route="r_{d}" begin="2700" end="3600" vehsPerHour="{v}" departLane="best"/>')
lines.append('</routes>')
open("routes.rou.xml", "w").write("\n".join(lines))
