import traci
from sumo_simulation import SumoSimulation
from data_writer import DataWriter


class LightsFunctions:

    def __init__(self, file, cars, steps: int = 100, data_writer = None):
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

        data["expected_traffic"] = self.cars
        y = LightsFunctions.get_metrics_function(data)
        
        if(self.data_writer): 
            data["x"] = x
            data["y"] = y
            self.data_writer.add_data(data)

        return y


    ### Escribir la formula para f(x) en este sitio
    @staticmethod
    def get_metrics_function(data):
        return 1 - (data["arrived_number"] / data["expected_traffic"]) if data["expected_traffic"] > 0 else 10**10
