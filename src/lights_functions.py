import traci
from sumo_simulation import SumoSimulation
from data_writer import DataWriter
from parameters import SIMULATION_TIME


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
    ### Escribir la formula para f(x) en este sitio, argumentos que tienen en data[]
    # arrived_number <-- Número de carros que salieron de la simulación
    # departed_number <-- Número de carros que entraron a la simulación
    # expected_traffic <-- Número de carros que se espera que se generen (total)
    # average_speed <-- Velocidad promedio
    # average_wait_time <-- Tiempo de espera promedio
    # average_travel_time <-- Promedio de viaje de los carros que salieron de la simulación

    @staticmethod
    def get_metrics_function(data):
        expected = data["expected_traffic"]
        
        if expected <= 0:
            return 10**10

        weights = {
            'arrival': 0.50,
            'speed': 0.20,
            'wait': 0.20,
            'travel': 0.10
        }

        # 1. Eficiencia de llegada
        arrival_penalty = (1 - data["arrived_number"]/expected) * weights['arrival']

        # 2. Velocidad promedio - Meta: 10 km/h (Ajustar después, pero yo creo que sí jalan 10km/h)
        speed_penalty = max(0, (10 - data["average_speed"])/10) * weights['speed']

        # 3. Tiempo de espera - Normalizado a 40% del tiempo total de simulación
        max_acceptable_wait = 0.4 * SIMULATION_TIME
        wait_penalty = (data["average_wait_time"]/max_acceptable_wait) * weights['wait']

        # 4. Tiempo de viaje - Relativo al tiempo total de simulación
        travel_penalty = (data["average_travel_time"]/SIMULATION_TIME) * weights['travel']

        # (0 = PERFECTO)
        total_score = (arrival_penalty + speed_penalty + wait_penalty + travel_penalty) * 100

        return total_score if total_score > 0 else 10**10

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
        
        data["x"] = x
        data["y"] = y
        if self.data_writer: 
            self.data_writer.add_data(data)
        return y, data
    
    def no_lights(self, visual = False):
        SUMO = SumoSimulation(self.file)
        SUMO.start_simulation(visual)
        if(not self.lights):
            return None

        data = SUMO.run_simulation(self.simulation_steps)
        SUMO.end_simulation()

        data["expected_traffic"] = self.cars
        y = LightsFunctions.get_metrics_function(data)
        
        if(self.data_writer): 
            print(self.lights)
            #data["x"] = x
            data["y"] = y
            self.data_writer.add_data(data)

        return y

