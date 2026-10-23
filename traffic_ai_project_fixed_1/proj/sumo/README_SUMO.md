# SUMO simulation setup (Windows)

SUMO is an independent traffic simulator. Install it from the official SUMO documentation:
https://sumo.dlr.de/docs/Installing/

After installing:
1. Open a new PowerShell window.
2. Check that these commands work:
   `sumo --version`
   `sumo-gui --version`
3. If Windows cannot find the commands, add the SUMO `bin` folder to PATH or set `SUMO_HOME` according to the official install guide.
4. Start with the official traffic-light TraCI tutorial:
   https://sumo.dlr.de/docs/Tutorials/TraCI4Traffic_Lights.html

## How to use SUMO for your report

- Create or import a small road network and traffic demand.
- Run a fixed-time baseline using a fixed signal program.
- Run an adaptive controller using Python + TraCI.
- Use the same network, vehicle demand, and random seed for both cases.
- Record travel time, waiting time, queue length, throughput, and number of completed trips.
- Repeat runs with multiple random seeds and report mean values.

TraCI has methods to step the simulation, query vehicles, and change traffic-light phases. Use the official tutorial as the source of truth for the SUMO version installed.

This starter pack does not claim to include a finished SUMO network or validated signal program. Do not connect it to real public-road signals.
