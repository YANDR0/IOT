from sumo_simulation import SumoSimulation
from lights_functions import LightsFunctions
from traffic_demand import TrafficDemand
from optimization import random_simulation, hill_simulation, swarm_simulation, genetic_simulation
from data_writer import DataWriter
import os

STEPS = 200

### Red, Entrada de tráfico, Salida de tráfico y tiempo
def generate_files(net, in_d, out_d, time):
    ### Genera las matrices de tráfico in_place en base a los diccionarios dados
    traffic = TrafficDemand.traffic_demand(in_d, out_d)
    ### Genera los archivos de la matriz de demanda (.taz y .od)
    taz, od = TrafficDemand.write_taz_od(in_d, out_d, traffic, time, "./assets")
    print()
    ### Genera los viajes en base a la matriz (.trip)
    trips = SumoSimulation.trip_from_od(taz, od, "./assets")
    ### Genera las rutas en base a los viajes (.rou)
    rou = SumoSimulation.rou_from_trip(net, trips, "./assets")
    print(rou)
    ### Genera el archivo de configuración en base a las rutas y red (.config)
    config = SumoSimulation.config_from_net_rou(os.path.basename(net), os.path.basename(rou), "./assets")

    ###Retorna el archivo de configuración necesario para la simualaciones
    return config

### Corre la simulación default sin modificaciones
def test_simulation(config, steps = STEPS) -> dict[str, float]:
    sumo = SumoSimulation(config)
    sumo.start_simulation(True)
    result = sumo.run_simulation(steps)
    sumo.end_simulation()
    return result

### Optimiza los semáforos y escribe los resultados 
def optimice_trafficlights(config, data = None) -> None:
    ### Objeto que escribe los resultados
    data_writer = DataWriter('default','data')
    ### Encargado de manejar la simulación y devolver resultados
    lights_function = LightsFunctions(config, steps=STEPS, data_writer=data_writer)
    ### Genera las listas mínimas y máximas de tiempo en base a la simulación () 
    x_low, x_high = lights_function.get_min_max(0, 150, 0, 5)

    ### Correr y optimizar la simulación en base a los 3 algoritmos
    data_writer.change_file('random')
    random_simulation(lights_function.all_lights, x_low, x_high, 20, data["random"] if data else None)
    data_writer.change_file('hill')
    hill_simulation(lights_function.all_lights, x_low, x_high, 20, data["hill"] if data else None)
    data_writer.change_file('swarm')
    swarm_simulation(lights_function.all_lights, x_low, x_high, 2, 10, data["swarm"] if data else None)
    data_writer.change_file('genetic')
    genetic_simulation(lights_function.all_lights, x_low, x_high, 2, 10, -5, 105)
    data_writer.write_file()

# Extrae las mejores configuraciones de los archivos y los devuelve como diccionario 
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

# En base a las mejores configuraciones, corre visualmente cada una de estas
def show_cases(config, data):
    simulation = LightsFunctions(config, 200)

    test_simulation(config, 200)

    print("random")
    simulation.all_lights(data['random']['x'], True)

    print("hill")
    simulation.all_lights(data['hill']['x'], True)

    print("swarm")
    simulation.all_lights(data['swarm']['x'], True)

    print("genetic")
    simulation.all_lights(data['genetic']['x'], True)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Se puede reemplazar con lectura de archivo o similar
    in_traffic = {"AD": 50}
    out_traffic = {"IL": 50}
    time = "0.0 0.01"
    network = "./assets/network.net.xml"

    configuration = generate_files(network, in_traffic, out_traffic, time)
    #optimice_trafficlights(configuration)
    #data = check_data()
    #show_cases(configuration, data)



    




