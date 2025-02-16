import traci
from sumo_simulation import SumoSimulation
from enum import Enum

class LightMode(Enum):
    SAME_TIME = 1 #Si fase es 1, todas las fases duran lo mismo
    BY_CHANGE = 2 #Si fase es 2, rojo y verde duran lo mismo, ambos amarillos duran lo mismo
    BY_COLOR = 3 #Si fase es 3, cada color dura lo suyo, verde, rojo y ambos amarillos
    BY_PHASE = 4 #Si fase es 4, cada etapa dura lo suyo, verde, rojo, amarillo 1, amarillo 2 

class LightsFunctions:
    #Fases del semáforo, verde, amarillo 1, 
    #phases = ["GrGr", "rGrG", "yryr", "ryry"]
    PHASES = ["GGggrrrrGGggrrrr", "rrrrGGggrrrrGGgg", "yyyyrrrryyyyrrrr", "rrrryyyyrrrryyyy"]

    def __init__(self, steps: int, color: bool, phases: int, show: bool = False):
        self.simulation_steps = steps
        self.color_together = color
        self.phases = phases
        self.show_lights = show

    @staticmethod
    def __print_lights(tl_dict: dict) -> None:
        for key, phases in tl_dict.items():
            print(f"{key}: ", end="")
            for phase in phases:
                print(phase.state, phase.duration, end=" ")
            print()

    def all_lights(self, x):      
        SUMO = SumoSimulation("assets/simulation.sumocfg")
        SUMO.start_simulation(False)

        tl = traci.trafficlight.getIDList()
        tl_num = len(tl)
        tl_dict = {id:[] for id in tl}
        
        for i in range(tl_num*self.phases):
            id = tl[i % tl_num if self.color_together else i//self.phases]
            
            if self.phases == LightMode.SAME_TIME.value:
                tl_dict[id] = [traci.trafficlight.Phase(x[i], p) for p in LightsFunctions.PHASES]   # 0, 1, 2 y 3
                continue

            step = len(tl_dict[id])
            
            if self.phases == LightMode.BY_CHANGE.value:
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.PHASES[step]))    # 0 o 2  
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.PHASES[step+1]))  # 1 o 3
                continue

            
            if step == 2 and self.phases == LightMode.BY_COLOR.value: 
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.PHASES[step+1]))  # 3 si phase == 3

            
            if self.phases != 3 or step < 4:
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.PHASES[step]))    # 0, 1, 2 o 3 si phases == 4 

        #priority_phases = {"GrGr": 0, "rGrG": 2, "yryr": 1, "ryry": 3}
        priority_phases = {"GGggrrrrGGggrrrr": 0, "rrrrGGggrrrrGGgg":2, "yyyyrrrryyyyrrrr":1, "rrrryyyyrrrryyyy":3}
        for key in tl_dict:
            tl_dict[key].sort(key=lambda x: priority_phases[x.state])
            traci.trafficlight.setProgramLogic(key, traci.trafficlight.Logic(key, 0, 0, tl_dict[key]))

        y = SUMO.run_simulation(self.simulationSteps)['traffic_flow']
        SUMO.end_simulation()
        if(self.show_lights): LightsFunctions.__print_lights(tl_dict)
        return 1 - y
