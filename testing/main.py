from sumo_simulation import SumoSimulation
from lights_functions import LightsFunctions
from traffic_demand import TrafficDemand
from optimization import randomMin, hill_simulation, swarm_simulation
from data_writer import DataWriter
import os



if __name__ == "__main__":
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)


