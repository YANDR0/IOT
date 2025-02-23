from sumo_simulation import SumoSimulation
from lights_functions import LightsFunctions
from optimization import randomMin, hill_simulation, swarm_simulation
import os, pickle

VISUAL = False

def probar() -> dict[str, float]:
    sumo = SumoSimulation("./assets/simulation.sumocfg")
    sumo.start_simulation(VISUAL)
    result = sumo.run_simulation(250)
    sumo.end_simulation()
    return result

def ejemplo_semaforo() -> None:

    lights_function = LightsFunctions(steps=250)
    x_low, x_high = lights_function.get_min_max(5, 150)

    y = probar()
    lights_function.change_parameters("random")
    x1, y1 = randomMin(lights_function.all_lights, x_low, x_high, 10)
    lights_function.change_parameters("hill")
    x2, y2 = hill_simulation(lights_function.all_lights, x_low, x_high, 10)
    lights_function.change_parameters("swarm")
    s = swarm_simulation(lights_function.all_lights, x_low, x_high, 2, 5)
    lights_function.file.close()

    print(y, y1, y2, s.BestY)

def ver_resultados():

    archivos = ["random", "hill", "swarm"]
    for f in archivos:
        data = []
        with open(f"./data/{f}.pkl", "rb") as archivo:
            while True:
                try:
                    data.append(pickle.load(archivo))
                except EOFError:
                    break
        
        print(f)
        for i in data: print(i)
        



if __name__ == "__main__":
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    ver_resultados()

    #ejemplo_semaforo()
