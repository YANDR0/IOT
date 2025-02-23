from sumo_simulation import SumoSimulation
from lights_functions import LightsFunctions
from optimization import randomMin, hill_simulation, swarm_simulation
import os, pickle

VISUAL = False

def probar() -> dict[str, float]:
    sumo = SumoSimulation("./assets/simulation.sumocfg", turn_data="./fieldwork_data.json")
    sumo.start_simulation(VISUAL)
    result = sumo.run_simulation(250)
    sumo.end_simulation()
    return result

def ejemplo_semaforo(data = None) -> None:

    lights_function = LightsFunctions(steps=250)
    x_low, x_high = lights_function.get_min_max(5, 150)

    y = probar()
    lights_function.change_parameters("random")
    x1, y1 = randomMin(lights_function.all_lights, x_low, x_high, 5, data["random"] if data else None)
    lights_function.change_parameters("hill")
    x2, y2 = hill_simulation(lights_function.all_lights, x_low, x_high, 5, data["hill"] if data else None)
    lights_function.change_parameters("swarm")
    s = swarm_simulation(lights_function.all_lights, x_low, x_high, 1, 5, data["swarm"] if data else None)
    lights_function.file.close()

    #print(y, y1, y2, s.BestY)

def ver_resultados():

    data = {"random": None, "hill": None, "swarm": None}
    for f in data:
        with open(f"./data/{f}.pkl", "rb") as archivo:
            while True:
                try:
                    info = pickle.load(archivo)
                    if(not data[f] or data[f]['traffic_flow'] > info['traffic_flow']):
                        data[f] = info
                except EOFError:
                    break
    return data
        

if __name__ == "__main__":
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    #data = ver_resultados()
    #for k in data:
    #    print(k, data[k])
    ejemplo_semaforo()

    #data = ver_resultados()
    #for k in data:
    #    print(k, data[k])
