from sumo_simulation import SumoSimulation
from lights_functions import LightsFunctions
from optimization import randomMin, hill_simulation, swarm_simulation
import os

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
    x1, y1 = randomMin(lights_function.all_lights, x_low, x_high, 100)
    x2, y2 = hill_simulation(lights_function.all_lights, x_low, x_high, 100)
    s = swarm_simulation(lights_function.all_lights, x_low, x_high, 100, 1000)

    print(y, y1, y2, s.BestY)

    


if __name__ == "__main__":
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    #print(probar())
    ejemplo_semaforo()
