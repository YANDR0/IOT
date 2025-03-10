from sumo_simulation import SumoSimulation
from lights_functions import LightsFunctions
from optimization import randomMin, hill_simulation, swarm_simulation
from data_writer import DataWriter
import os

def generate_files():
    net = SumoSimulation.net_from_nod_edg("./assets/nodes.nod.xml", "./assets/edges.edg.xml", "./assets")
    trips = SumoSimulation.random_trips(net, "./assets/randomTrips.py", "./assets")
    rou = SumoSimulation.rou_from_trip(net, trips, "./assets")
    config = SumoSimulation.config_from_net_rou(net.split("/")[-1], rou.split("/")[-1], "./assets")
    return config

def test_simulation(config, steps = 250, visual = False) -> dict[str, float]:
    sumo = SumoSimulation(config)
    sumo.start_simulation(visual)
    result = sumo.run_simulation(steps)
    sumo.end_simulation()
    return result

def optimice_trafficlights(data = None) -> None:

    data_writer = DataWriter('default','data')
    lights_function = LightsFunctions("./assets/simulation.sumocfg", steps=100, data_writer=data_writer)
    x_low, x_high = lights_function.get_min_max(5, 150)

    data_writer.change_file('random')
    x1, y1 = randomMin(lights_function.all_lights, x_low, x_high, 1000, data["random"] if data else None)
    data_writer.change_file('hill')
    x2, y2 = hill_simulation(lights_function.all_lights, x_low, x_high, 1000, data["hill"] if data else None)
    data_writer.change_file('swarm')
    s = swarm_simulation(lights_function.all_lights, x_low, x_high, 5, 200, data["swarm"] if data else None)
    data_writer.write_file()

def check_data():
    data_writer = DataWriter('default','data')  
    data = {}

    data_writer.change_file('random')
    data_writer.read_file()
    data['random'] = data_writer.best

    data_writer.change_file('hill')
    data_writer.read_file()
    data['hill'] = data_writer.best

    data_writer.change_file('swarm')
    data_writer.read_file()
    data['swarm'] = data_writer.best

    return data

def show_cases(data):
    simulation = LightsFunctions("./assets/simulation.sumocfg", 100)

    test_simulation("./assets/simulation.sumocfg", 100)

    print("random")
    simulation.all_lights(data['random']['x'], True)

    print("hill")
    simulation.all_lights(data['hill']['x'], True)

    print("swarm")
    simulation.all_lights(data['swarm']['x'], True)



if __name__ == "__main__":
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    #optimice_trafficlights()

    #config = generate_files()
    #print(config)
    #test_simulation("./assets/simulation.sumocfg", visual=True)

    #data = check_data()
    #print(data)
    #show_cases(data)

    archivo1 = SumoSimulation.random_trips("./assets/red_hidalgo-federalismo.net.xml", "./assets/randomTrips.py", "./assets/algo.trips.xml", False)
    archivo2 = SumoSimulation.rou_from_trip("./assets/red_hidalgo-federalismo.net.xml", archivo1, "./assets/algo.rou.xml", False)
    #Todo el show de OD
    #SumoSimulation.trip_from_od("./assets/network.net.xml", "./assets/od_matrix.od.xml", "./assets")