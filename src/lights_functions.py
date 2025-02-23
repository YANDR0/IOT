import traci, pickle
from sumo_simulation import SumoSimulation


class LightsFunctions:

    def __init__(self, steps: int = 100, function = "default"):
        self.simulation_steps = steps
        self.lights = None
        self.phases_number = 0
        self.function = function
        self.file = open(f"./data/{function}.pkl", "ab") 
            
        SUMO = SumoSimulation("assets/simulation.sumocfg")
        SUMO.start_simulation(False)
        self.get_ligths_phases(SUMO)
        SUMO.end_simulation()

    def change_parameters(self, function):
        self.file.close()
        self.function = function
        self.file = open(f"./data/{function}.pkl", "ab")     

    def write_data(self, data):
        pickle.dump(data, self.file)

    def get_ligths_phases(self, simulation: SumoSimulation):
        simulation.run_simulation(0)
        self.lights, self.phases_number = simulation.get_lights()

    def get_min_max(self, min_time, max_time):
        return [min_time for _ in range(self.phases_number)], [max_time for _ in range(self.phases_number)]

    def all_lights(self, x):
        SUMO = SumoSimulation("assets/simulation.sumocfg")
        SUMO.start_simulation(False)
        if(not self.lights):
            self.get_ligths_phases(SUMO)

        i = 0
        for key in self.lights:
            new_phases = []
            for phase in self.lights[key]:
                new_phases.append(traci.trafficlight.Phase(x[i], phase))
                i += 1

            logic = traci.trafficlight.Logic(key, 0, 0, new_phases)
            traci.trafficlight.setProgramLogic(key, logic)
            traci.trafficlight.setProgram(key, key)

        data = SUMO.run_simulation(self.simulation_steps)
        SUMO.end_simulation()

        data["x"] = x
        self.write_data(data)
        y = data["traffic_flow"]
        return 1 - y
