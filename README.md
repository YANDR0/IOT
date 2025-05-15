Index

* [General Description](#general-description)
* [Project Structure](#project-structure)
* [Main Modules](#main-modules)
* [Simulation Parameters](#simulation-parameters)
* [Installation and Setup](#installation-and-setup)
* [Usage Examples](#usage-examples)

## General Description

This project provides a modular platform for simulating and optimizing traffic signal control in urban traffic networks using SUMO and TraCI. It employs bio-inspired algorithms (Random Search, Hill Climbing, Particle Swarm Optimization, Simulated Annealing, and Genetic Algorithms) to adjust traffic light phase durations, aiming to improve metrics such as vehicle throughput, average speed, and wait time. Results are stored in JSON files for subsequent analysis and comparison.

## Project Structure

```plaintext
.
├── pyproject.toml
├── README.md
└── src/
    ├── assets/                # Network, routes, and generated configuration
    ├── data/                  # Simulation and optimization outputs (.json)
    ├── data_writer.py         # Result persistence management
    ├── lights_functions.py    # Traffic light logic and metric calculation
    ├── main.py                # Generation, testing, and optimization functions
    ├── optimization/          # Algorithm implementations
    ├── parameters.py          # Global simulation parameters
    ├── randomTrips.py         # Trip generation
    ├── sumo_simulation.py     # SUMO/TraCI wrapper
    ├── traffic_demand.py      # OD matrix and TAZ/OD file generation
    └── utils.py               # Helper functions
``` 

## Main Modules



### sumo_simulation.py

* Network and route generation (`netconvert`, `duarouter`, `od2trips`).
* Simulation lifecycle control (`start_simulation`, `run_simulation`, `end_simulation`).
* Extraction of metrics and traffic light states.

### traffic_demand.py

* Reading traffic demand CSV files.
* Balancing incoming and outgoing volumes.
* Generating OD matrices and TAZ/OD files.

### lights_functions.py

* Retrieving current traffic light phases.
* Objective function for evaluating configurations.
* Applying new phase timings and computing metrics.

### data_writer.py

* Iterative storage of results in JSON.
* Reading and extracting the best configuration.

### optimization/

Contains implementations of:

* Random Search (`random_simulation`)
* Hill Climbing (`hill_simulation`)
* Particle Swarm Optimization (`swarm_simulation`)
* Simulated Annealing (`tsp_sa`)
* Genetic Algorithms (`genetic_simulation`)

Each function accepts the traffic-light interface, minimum and maximum time ranges, and returns optimized phase vectors.

### main.py

High-level utility functions:

* `generate_files(net, in_d, out_d, time)`: Generates `.taz`, `.od`, `.trip`, `.rou`, and `.sumocfg` files.
* `test_simulation(config, steps)`: Runs a test simulation and returns metrics.
* `optimice_trafficlights(config, cars, data=None)`: Runs optimization (Simulated Annealing by default) and saves results.
* `check_data()`: Reads previous results for each algorithm and returns the best configurations.
* `show_cases(config, data)`: Visually replays the optimal configurations.

### For More Detailed Information

For more comprehensive information about the methods and classes in our code, please refer to our detailed [Documentation.md](Documentation.md) file. This document provides in-depth explanations of all components in the system.

The documentation includes complete descriptions of the classes, methods, parameters, and return values, making it easier to understand and use the SUMO Traffic Simulation system.

## Simulation Parameters

Defaults are defined in `parameters.py`:

| Parameter                     | Description                               |
| ----------------------------- | ----------------------------------------- |
| `STEPS`                       | Number of simulation steps per run        |
| `GREEN_RED_MAX_TIME_SECONDS`  | Max green/red phase duration (seconds)    |
| `GEEEN_RED_MIN_TIME_SECONDS`  | Min green/red phase duration (seconds)    |
| `YELLOW_MAX_TIME_SECONDS`     | Max yellow phase duration (seconds)       |
| `YELLO_MIN_TIME_SECONDS`      | Min yellow phase duration (seconds)       |
| `START_TIME`, `END_TIME`      | Simulation start and end times            |

## Installation and Setup

1. Install SUMO and add it to your `PATH` ([https://sumo.dlr.de/docs/Downloads.php](https://sumo.dlr.de/docs/Downloads.php)).
2. Install Python 3.12 or higher.
3. Install TraCI:
   ```bash
   pip install traci
   ```

## Usage Examples

Below are examples of how to use the project's functions and modules.

### 1. Generating Configuration Files

```python
from src.main import generate_files
from src.traffic_demand import TrafficDemand

in_d = TrafficDemand.read_csv("./assets/entrada.csv")
out_d = TrafficDemand.read_csv("./assets/salida.csv")
time_window = "08:00 09:00"
config = generate_files("./assets/map.net.xml", in_d, out_d, time_window)
```

### 2. Running a Test Simulation

```python
from src.sumo_simulation import SumoSimulation

sumo = SumoSimulation(config)
sumo.start_simulation(False)
result = sumo.run_simulation(100)
sumo.end_simulation()
print(result)
```

### 3. Simulated Annealing Optimization

```python
from src.data_writer import DataWriter
from src.lights_functions import LightsFunctions
from src.optimization.simmulated_annealing import tsp_sa

# Setup
data_writer = DataWriter('sa', 'data')
lf = LightsFunctions(config, cars, steps=100, data_writer=data_writer)
x_low, x_high = lf.get_min_max(10, 60, 3, 6)

# Run optimization
_, _, sa_results = tsp_sa(lf.all_lights, x_low, x_high, max_iter=100)
for entry in sa_results:
    data_writer.add_data(entry)
data_writer.write_file()
```

### 4. Random Search Optimization

```python
from src.data_writer import DataWriter
from src.lights_functions import LightsFunctions
from src.optimization.random import random_simulation

writer = DataWriter('random', 'data')
lf = LightsFunctions(config, cars, steps=100, data_writer=writer)
x_low, x_high = lf.get_min_max(10, 60, 3, 6)
_, _, random_results = random_simulation(
    lf.all_lights, x_low, x_high, iterations=50
)
for entry in random_results:
    writer.add_data(entry)
writer.write_file()
```

### 5. Hill Climbing Optimization

```python
from src.data_writer import DataWriter
from src.lights_functions import LightsFunctions
from src.optimization.hill_climbing import hill_simulation

writer = DataWriter('hill', 'data')
lf = LightsFunctions(config, cars, steps=100, data_writer=writer)
x_low, x_high = lf.get_min_max(10, 60, 3, 6)
hill_simulation(lf.all_lights, x_low, x_high, max_iter=100)
```

### 6. Particle Swarm Optimization

```python
from src.data_writer import DataWriter
from src.lights_functions import LightsFunctions
from src.optimization.pso import swarm_simulation

writer = DataWriter('swarm', 'data')
lf = LightsFunctions(config, cars, steps=100, data_writer=writer)
x_low, x_high = lf.get_min_max(10, 60, 3, 6)
swarm_simulation(
    lf.all_lights, x_low, x_high, swarm_size=20, max_iter=100
)
```

### 7. Genetic Algorithm Optimization

```python
from src.data_writer import DataWriter
from src.lights_functions import LightsFunctions
from src.optimization.genetic import genetic_simulation

writer = DataWriter('genetic', 'data')
lf = LightsFunctions(config, cars, steps=100, data_writer=writer)
x_low, x_high = lf.get_min_max(10, 60, 3, 6)
_, _, genetic_results = genetic_simulation(
    lf.all_lights, x_low, x_high,
    n=100,
    m=50,
    -5, #Lower bound
    105 #Upper bound
)
for entry in genetic_results:
    writer.add_data(entry)
writer.write_file()
```

### 8. Visualizing Optimized Cases

```python
from src.lights_functions import LightsFunctions
from src.data_writer import DataWriter

# Read best configuration from JSON
writer = DataWriter('sa', 'data')
writer.read_file()
best = writer.best

# Visualize in SUMO
lfs = LightsFunctions(config, cars, steps=200)
lfs.all_lights(best['x'], visual=True)
```
