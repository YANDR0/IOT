from sumo_simulation import SumoSimulation
from lights_functions import LightsFunctions, LightMode
import os

VISUAL = False


def probar() -> dict[str, float]:
    sumo = SumoSimulation("./assets/simulation.sumocfg")
    sumo.start_simulation(VISUAL)
    result = sumo.run_simulation(250)
    print(result)
    sumo.end_simulation()
    return result


def ejemplo_semaforo() -> None:
    test_cases = [
        ([11, 21, 31, 41], True, 3),
        ([11, 21, 31, 41, 12, 22, 32, 42], True, 2),
        ([11, 21, 31, 41, 12, 22, 32, 42, 13, 23, 33, 43], True, 1),
        ([11, 21, 31, 41, 12, 22, 32, 42, 13, 23, 33, 43, 14, 24, 34, 44], True, 2),
    ]

    for data, color, phase_mode in test_cases:
        lights = LightsFunctions(steps=250, color=color, phases=phase_mode, show=False)
        print(f"Traffic flow (phase mode {phase_mode}: {lights.all_lights(data)}")


if __name__ == "__main__":
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print(probar())
    ejemplo_semaforo()
