from sumo_simulation import SumoSimulation
from lights_functions import LightsFunctions
from optimization import randomMin, hill_simulation, swarm_simulation
from data_writer import DataWriter
import os

VISUAL = False

def generate_files():
    net = SumoSimulation.net_from_nod_edg("./assets/nodes.nod.xml", "./assets/edges.edg.xml", "./assets")
    trips = SumoSimulation.random_trips(net, "./assets/randomTrips.py", "./assets")
    rou = SumoSimulation.rou_from_trip(net, trips, "./assets")
    config = SumoSimulation.config_from_net_rou(net.split("/")[-1], rou.split("/")[-1], "./assets")
    return config

def test_simulation(config, steps = 250) -> dict[str, float]:
    sumo = SumoSimulation(config)
    sumo.start_simulation(VISUAL)
    result = sumo.run_simulation(steps)
    sumo.end_simulation()
    return result

def optimice_trafficlights(data = None) -> None:

    data_writer = DataWriter('default','data')
    lights_function = LightsFunctions(steps=100, data_writer=data_writer)
    x_low, x_high = lights_function.get_min_max(5, 150)

    data_writer.change_file('random')
    x1, y1 = randomMin(lights_function.all_lights, x_low, x_high, 5, data["random"] if data else None)
    data_writer.change_file('hill')
    x2, y2 = hill_simulation(lights_function.all_lights, x_low, x_high, 5, data["hill"] if data else None)
    data_writer.change_file('swarm')
    s = swarm_simulation(lights_function.all_lights, x_low, x_high, 1, 5, data["swarm"] if data else None)
    data_writer.write_file()

def check_data():
    data_writer = DataWriter('default','data')  

    data_writer.change_file('random')
    data_writer.read_file()
    print(data_writer.best)

    data_writer.change_file('hill')
    data_writer.read_file()
    print(data_writer.best)

    data_writer.change_file('swarm')
    data_writer.read_file()
    print(data_writer.best)

    print(data_writer.data)
        
if __name__ == "__main__":
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    config = generate_files()
    #print(config)
    #test_simulation("./assets/simulation.sumocfg")




