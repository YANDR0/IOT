from sumo_simulation import SumoSimulation
from lights_functions import LightsFunctions
from traffic_demand import TrafficDemand
from optimization import random_simulation, hill_simulation, swarm_simulation, genetic_simulation
from data_writer import DataWriter
import os


VISUAL = True

def generate_files():
    net = SumoSimulation.net_from_nod_edg("./assets/nodes.nod.xml", "./assets/edges.edg.xml", "./assets")
    trips = SumoSimulation.random_trips(net, "./randomTrips.py", "./assets")
    rou = SumoSimulation.rou_from_trip(net, trips, "./assets")
    config = SumoSimulation.config_from_net_rou(os.path.basename(net), os.path.basename(rou), "./assets")
    return config

def generate_files_2(in_d, out_d):
    traffic = TrafficDemand.traffic_demand(in_d, out_d)
    taz, od = TrafficDemand.write_taz_od(in_d, out_d, traffic, "0.0 0.01", "./assets")
    net = SumoSimulation.net_from_nod_edg("./assets/nodes.nod.xml", "./assets/edges.edg.xml", "./assets")
    trips = SumoSimulation.trip_from_od("./assets/tazes.taz.xml", "./assets/matriz.od", "./assets")
    rou = SumoSimulation.rou_from_trip(net, trips, "./assets")
    config = SumoSimulation.config_from_net_rou(os.path.basename(net), os.path.basename(rou), "./assets")
    return config

def test_simulation(config, steps = 250) -> dict[str, float]:
    sumo = SumoSimulation(config)
    sumo.start_simulation(VISUAL)
    result = sumo.run_simulation(steps)
    sumo.end_simulation()
    return result

def optimice_trafficlights(data = None) -> None:
    data_writer = DataWriter('default','data')
    lights_function = LightsFunctions("./assets/simulation.sumocfg", steps=200, data_writer=data_writer)
    x_low, x_high = lights_function.get_min_max(0, 150, 0, 5)

    data_writer.change_file('random')
    x1, y1 = random_simulation(lights_function.all_lights, x_low, x_high, 100, data["random"] if data else None)
    data_writer.change_file('hill')
    x2, y2 = hill_simulation(lights_function.all_lights, x_low, x_high, 100, data["hill"] if data else None)
    data_writer.change_file('swarm')
    s = swarm_simulation(lights_function.all_lights, x_low, x_high, 5, 20, data["swarm"] if data else None)
    data_writer.change_file('genetic')
    a = genetic_simulation(lights_function.all_lights, x_low, x_high, 5, 20, -5, 105)
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

    data_writer.change_file('genetic')
    data_writer.read_file()
    data['genetic'] = data_writer.best

    return data

def show_cases(data):
    simulation = LightsFunctions("./assets/simulation.sumocfg", 200)

    test_simulation("./assets/simulation.sumocfg", 200)

    print("random")
    simulation.all_lights(data['random']['x'], True)

    print("hill")
    simulation.all_lights(data['hill']['x'], True)

    print("swarm")
    simulation.all_lights(data['swarm']['x'], True)

    print("genetic")
    simulation.all_lights(data['genetic']['x'], True)

    


if __name__ == "__main__":
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)


    generate_files_2({"AD": 100}, {"IL": 50, "HK": 50})
    optimice_trafficlights()
    data = check_data()
    show_cases(data)


    






