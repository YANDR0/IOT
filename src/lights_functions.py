import traci
from sumo_simulation import SumoSimulation
from data_writer import DataWriter


class LightsFunctions:

    metric_function = None

    def __init__(self, file, cars, steps: int = 100, data_writer = None):
        if(not LightsFunctions.metric_function):
            LightsFunctions.metric_function = LightsFunctions.get_metrics_function(100, 0, 0)
        self.cars = cars
        self.simulation_steps = steps
        self.lights = None
        self.phases_number = 0
        self.data_writer: DataWriter = data_writer 
        self.file = file
            
        SUMO = SumoSimulation(self.file)
        SUMO.start_simulation(False)
        self.get_ligths_phases(SUMO)
        SUMO.end_simulation()

    def get_ligths_phases(self, simulation: SumoSimulation):
        simulation.run_simulation(0)
        self.lights, self.phases_number = simulation.get_lights()

    def get_min_max(self, min_time_rg, max_time_rg, min_time_y = None, max_time_y = None):
        min_time = []
        max_time = []

        for key in self.lights:
            for phase in self.lights[key]:
                min_time.append(min_time_y if min_time_y and 'y' in phase else min_time_rg)
                max_time.append(max_time_y if max_time_y and 'y' in phase else max_time_rg)

        return min_time, max_time

    def all_lights(self, x, visual = False):
        SUMO = SumoSimulation(self.file)
        SUMO.start_simulation(visual)
        if(not self.lights):
            return None

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

        y = LightsFunctions.metric_function(data)
        data["expected_traffic"] = self.cars
        data["x"] = x
        data["y"] = y
        if(self.data_writer): self.data_writer.add_data(data)
        return y

    ### Acá podemos describir la función de Y, la cosa es que no sé que nos da avg_wait_time o avg_speed
    # O como normalizarlos en general :v
    @staticmethod
    def get_metrics_function(w1 = 1, w2 = 1, w3 = 1):
        return lambda data: (1 - data["traffic_flow"]) * w1 + data["avg_wait_time"] * w2 + (1/data["avg_speed"]) * w3
