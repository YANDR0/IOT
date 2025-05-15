# SUMO Traffic Simulation System Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [SumoSimulation Class](#sumosimulation-class)
3. [TrafficDemand Class](#trafficdemand-class)
4. [DataWriter Class](#datawriter-class)
5. [LightsFunctions Class](#lightsfunctions-class)

---

## Introduction

This documentation covers a framework designed to work with SUMO (Simulation of Urban MObility), an open-source traffic simulation software. The framework consists of several classes that facilitate creating traffic simulations, managing traffic demand, handling traffic light configurations, and recording simulation results.

---

## SumoSimulation Class

This class is used to control the execution of simulations.

### Static Methods

```python
net_from_nod_edg(nodes, edges, dest)
```

Generates a net.xml file based on nod.xml and edg.xml files using SUMO's netconvert command.

**Arguments:**
- `nodes` (str): Path to the nod.xml file
- `edges` (str): Path to the edg.xml file
- `dest` (str): Destination path for the resulting net.xml file (defaults to network.net.xml if not specified)

**Returns:**
- `str`: Path to the network file

```python
net_from_osm(open_street, dest)`
```

Generates a net.xml file based on an OpenStreetMap file using SUMO's netconvert command.

**Arguments:**
- `open_street` (str): Path to the OSM file
- `dest` (str): Destination path for the resulting net.xml file (defaults to network.net.xml if not specified)

**Returns:**
- `str`: Path to the network file

```python
trip_from_od(taz, matrix, dest)
```

Generates a trips.xml file from an origin-destination matrix.

**Arguments:**
- `taz` (str): Path to the TAZ file
- `matrix` (str): Path to the OD matrix file
- `dest` (str): Destination path for the resulting trips.xml file

**Returns:**
- `str`: Path to the trips file

```python
random_trips(network, random, dest)
```

Generates a trips.xml file with random trips based on a network file using SUMO's randomTrips.py script.

**Arguments:**
- `network` (str): Path to the net.xml file
- `random` (str): Path to the randomTrips.py script
- `dest` (str): Destination path for the resulting trips.xml file (defaults to traffic.trips.xml if not specified)

**Returns:**
- `str`: Path to the trips file

```python
rou_from_trip(network, trips, dest)
```

Generates a rou.xml file based on trips.xml using SUMO's duarouter command.

**Arguments:**
- `network` (str): Path to the net.xml file
- `trips` (str): Path to the trips.xml file
- `dest` (str): Destination path for the resulting rou.xml file (defaults to routes.rou.xml if not specified)

**Returns:**
- `str`: Path to the routes file

```python
config_from_net_rou(network, routes, dest)
```

Generates a SUMO configuration file (sumocfg) based on net.xml and rou.xml files.

**Arguments:**
- `network` (str): Path to the net.xml file
- `routes` (str): Path to the rou.xml file
- `dest` (str): Destination path for the resulting sumocfg file (defaults to simulation.sumocfg if not specified)

**Returns:**
- `str`: Path to the configuration file

### Instance Methods

```python
__init__(self, configuration="")
```

Constructor for the SumoSimulation class.

**Arguments:**
- `configuration` (str): Path to the sumocfg file

```python
set_files(self, config)
```

Assigns a sumocfg file path to the object.

**Arguments:**
- `config` (str): Path to the sumocfg file

```python
start_simulation(self, visual)
```

Prepares the SUMO simulation for starting based on the configuration file.

**Arguments:**
- `visual` (bool): Flag specifying whether to run the simulation visually with sumo-gui or directly with sumo

```python
run_simulation(self, steps)
```

Executes the specified simulation for a number of steps in SUMO.

**Arguments:**
- `steps` (int): Number of simulation cycles to execute

**Returns:**
- `dict[str, float]`: Dictionary with simulation results, containing:
  - `arrived_number`: Number of vehicles that exited the network
  - `departed_number`: Number of vehicles that entered the network
  - `average_speed`: Average speed of vehicles
  - `average_wait_time`: Average waiting time of vehicles
  - `average_travel_time`: Average travel time of vehicles

```python
end_simulation(self)
```

Correctly finalizes and closes the simulation.

```python
get_lights(self)
```

Provides information about traffic light configurations in the simulation.

**Returns:**
- `dict[str, list]`: Dictionary with IDs and phases of each traffic light
- `int`: Total number of phases across all traffic lights

---

## TrafficDemand Class

This class handles reading traffic data from CSV files and generating traffic based on demand matrices. It primarily works with dictionaries where keys represent street IDs and values represent the number of vehicles on those streets.

### Static Methods

```python
read_csv(route)
```

Reads vehicular traffic data from a CSV file with one column representing street IDs and another representing vehicle counts.

**Arguments:**
- `route` (str): Path to the CSV file

**Returns:**
- `dict[str, int]`: Dictionary with street IDs and vehicle counts

```python
match_traffic(traffic_1, traffic_2)
```

Equalizes the total values of two traffic dictionaries proportionally (modifies dictionaries in place).

**Arguments:**
- `traffic_1` (dict[str, int]): Dictionary with street IDs and vehicle counts
- `traffic_2` (dict[str, int]): Dictionary with street IDs and vehicle counts

```python
traffic_demand(incoming_traffic, outgoing_traffic)`
```

Distributes traffic proportionally based on dictionaries of incoming and outgoing data.

**Arguments:**
- `incoming_traffic` (dict[str, int]): Dictionary with street IDs and counts of vehicles entering the system
- `outgoing_traffic` (dict[str, int]): Dictionary with street IDs and counts of vehicles exiting the system

**Returns:**
- `list[tuple(str, str, int)]`: List of triplets containing origin ID, destination ID, and vehicle count for that journey

```python
random_traffic_demand(incoming_traffic, outgoing_traffic)`
```

Distributes traffic randomly based on dictionaries of incoming and outgoing data.

**Arguments:**
- `incoming_traffic` (dict[str, int]): Dictionary with street IDs and counts of vehicles entering the system
- `outgoing_traffic` (dict[str, int]): Dictionary with street IDs and counts of vehicles exiting the system

**Returns:**
- `list[tuple(str, str, int)]`: List of triplets containing origin ID, destination ID, and vehicle count for that journey

```python
write_taz_od(incoming_traffic, outgoing_traffic, traffic, time, dest)`
```

Writes TAZ (Traffic Assignment Zone) and OD (Origin-Destination) matrix files required for SUMO.

**Arguments:**
- `incoming_traffic` (dict[str, int]): Dictionary with street IDs and counts of vehicles entering the system
- `outgoing_traffic` (dict[str, int]): Dictionary with street IDs and counts of vehicles exiting the system
- `traffic` (list): Traffic demand data
- `time` (str): Time representation for the OD matrix
- `dest` (str): Destination path for output files

**Returns:**
- `tuple(str, str)`: Paths to the TAZ and OD matrix files

---

## DataWriter Class

This class is used to record simulation results through the LightsFunctions class in JSON files. It stores data from all simulations in a list of dictionaries and separately records the best case.

### Instance Methods

```python
__init__(self, file_name, directory)`
```

Constructor for the DataWriter class.

**Arguments:**
- `file_name` (str): Name of the JSON file to create or modify
- `directory` (str): Path to the JSON file

```python
read_file(self)`
```

Reads the JSON file specified in the object and returns a dictionary with that data.

**Returns:**
- `dict[str, dict]`: Dictionary containing the main data for each simulation and direct access to the best simulation

```python
write_file(self)`
```

Writes the data stored within the object to the previously specified file.

```python
overwrite_best(self)`
```

Overwrites the data stored within the object in the previously specified file.

```python
add_data(self, data)`
```

Stores information from each simulation within the object.

**Arguments:**
- `data` (dict): Dictionary containing the resulting information from each simulation

```python
change_file(self, file_name, directory, write)`
```

Changes the current JSON file being worked with within the object.

**Arguments:**
- `file_name` (str): Name of the new JSON file to modify
- `directory` (str): Directory of the new JSON file to modify (remains the same if not provided)
- `write` (bool): Boolean indicating whether data registered so far will be added to the previous file or discarded

```python
set_best(self)`
```

Updates the value of the best simulation within the object.

---

## LightsFunctions Class

This class acts as a mediator between the SumoSimulation class and optimization algorithms, converting input x into something usable within the simulation and then transforming simulation results into something readable for optimization algorithms.

### Instance Methods

```python
__init__(self, file, cars, steps=100, data_writer=None)`
```

Creates an instance of the LightsFunctions class.

**Arguments:**
- `file` (str): Path to the configuration file to use in the simulation
- `cars` (int): Total number of vehicles in the simulation
- `steps` (int): Number of simulation steps
- `data_writer` (DataWriter): DataWriter instance for saving results

```python
get_metrics_function(data)`
```

Transforms simulation variables such as average speed into a single output for optimization algorithms.

**Arguments:**
- `data` (dict): Simulation data obtained from SumoSimulation

**Returns:**
- `float`: Result of operations (optimization score)

```python
get_ligths_phases(self, simulation)`
```

Obtains the list of all phases for each traffic light in the current simulation and stores it within the object.

**Arguments:**
- `simulation` (SumoSimulation): Simulation from which to obtain the phases

```python
get_min_max(self, min_time_rg, max_time_rg, min_time_y=None, max_time_y=None)`
```

Returns two lists of size n with minimum and maximum time values, where n is the total number of stages for each traffic light.

**Arguments:**
- `min_time_rg` (float): Minimum time for stages with only red and green lights
- `max_time_rg` (float): Maximum time for stages with only red and green lights
- `min_time_y` (float): Minimum time for stages with yellow lights (uses min_time_rg if not specified)
- `max_time_y` (float): Maximum time for stages with yellow lights (uses max_time_rg if not specified)

**Returns:**
- `list[float]`: List of minimum times for each stage
- `list[float]`: List of maximum times for each stage

```python
all_lights(self, x, visual=False)`
```

Executes the simulation modifying the time of each traffic light phase based on the x list of numbers.

**Arguments:**
- `x` (list[float]): List of times for each traffic light phase
- `visual` (bool): Boolean indicating whether the simulation will be executed with a graphical interface

**Returns:**
- `float`: Result of get_metrics_function operations to minimize
- `dict`: Detailed simulation data

```python
no_lights(self, visual=False)`
```

Runs a simulation without modifying traffic light timings (baseline).

**Arguments:**
- `visual` (bool): Boolean indicating whether the simulation will be executed with a graphical interface

**Returns:**
- `float`: Optimization score