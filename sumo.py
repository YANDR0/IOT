import subprocess
import traci
import optimization     ### Es el de Yandro, luego vemos si usamos otro o que
from os import path


# Administra la simulación de SUMO
class SumoSimulation():

    # Dan a entender la etapa de la simulación y evitan correr los que no
    CANNOT_START = 0
    CAN_START = 1
    CAN_RUN = 2
    RUNNING = 3

    # Crea administrador de la simulación
    def __init__(self, configuration):
        self.sumoConfiguration = configuration
        self.step = SumoSimulation.CAN_START if path.exists(self.sumoConfiguration) else SumoSimulation.CANNOT_START

    # Crea los archivos de red y tráfico, debería crear la configuración también pero meh
    def generate_files(self, nodes, edges, random):
        CMDNetwork = f"netconvert --node-files {nodes} --edge-files {edges} --tls.guess true --output-file=assets/network.net.xml".split()
        CMDTrips = f"python {random} -n assets/network.net.xml -o assets/traffic.trips.xml --fringe-factor 50"
        CMDTraffic = "duarouter -n assets/network.net.xml -t assets/traffic.trips.xml -o assets/traffic.rou.xml"

        subprocess.run(CMDNetwork)
        subprocess.run(CMDTrips)
        subprocess.run(CMDTraffic)
        self.step = SumoSimulation.CAN_RUN

    # Inicia la simulación, ya sea de forma visual o no, después de esto se pueden configurar 
    def start_simulation(self, visual):
        if(self.step < SumoSimulation.CAN_START): return
        cmd = ["sumo-gui" if visual else "sumo", "-c", self.sumoConfiguration]
        traci.start(cmd)
        self.step = SumoSimulation.CAN_RUN

    # Corre la simulación un total de N pasos y obtiene la razón de carros que terminaron (Podemos cambiar parámetro)
    def run_simulation(self, steps):
        if(self.step < SumoSimulation.CAN_RUN): return
        self.step = SumoSimulation.RUNNING
        
        totalEnds = 0
        totalStarts = 0
        for _ in range(steps):
            traci.simulationStep()
            totalEnds += traci.simulation.getArrivedNumber()
            totalStarts  += traci.simulation.getDepartedNumber()

        return totalEnds/totalStarts
    
    # Termina la simulación
    def end_simulation(self):
        if(self.step < SumoSimulation.RUNNING): return
        traci.close()
        self.step = SumoSimulation.CAN_START


# Configurar las funciones para pasarselas a los algoritmos de optimización (f(x))
class LightsFunctions():

    # Fases del semáforo, verde, amarillo 1, 
    #phases = ["GrGr", "rGrG", "yryr", "ryry"]
    phases = ["GGggrrrrGGggrrrr", "rrrrGGggrrrrGGgg", "yyyyrrrryyyyrrrr", "rrrryyyyrrrryyyy"]

    SAME_TIME = 1   #Si fase es 1, todas las fases duran lo mismo
    BY_CHANGE = 2   #Si fase es 2, rojo y verde duran lo mismo, ambos amarillos duran lo mismo
    BY_COLOR = 3    #Si fase es 3, cada color dura lo suyo, verde, rojo y ambos amarillos
    BY_PHASE = 4    #Si fase es 4, cada etapa dura lo suyo, verde, rojo, amarillo 1, amarillo 2 

    # Crea administrador de las funciones, steps define los pasos o ciclos de la simulación
    # color si los datos de x están juntos por color y phases cuantos tiempos se dieron
    def __init__(self, steps, color, phases, show = False):
        self.simulationSteps = steps  #Cantidad de pasos en la simulación
        self.color_toguether = color  #Parámetros están juntos por color o por semáforo
        self.phases = phases     #Cuales ciclos duran igual
        self.show_lights = show

    @staticmethod
    def __print_lights(x):
        for i in x:
            print(i, " ", end="")
            for j in x[i]:
                print(j.state, j.duration, end=" ")
            print()

    def get_min_max(self, *args):
        pass

    
    # Recibe los tiempos y configura los semáforos de manera individual en base a eso
    def all_lights(self, x):      
        SUMO = SumoSimulation("assets/simulation.sumocfg")
        SUMO.start_simulation(False)

        tl = traci.trafficlight.getIDList()
        tl_num = len(tl)
        tl_dict = {id:[] for id in tl}
        
        
        for i in range(tl_num*self.phases):
            id = tl[i % tl_num if self.color_toguether else i//self.phases]

            
            if(self.phases == 1):
                tl_dict[id] = [traci.trafficlight.Phase(x[i], p) for p in LightsFunctions.phases]   # 0, 1, 2 y 3
                continue

            step = len(tl_dict[id])
            
            if(self.phases == 2):
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.phases[step]))    # 0 o 2  
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.phases[step+1]))  # 1 o 3
                continue

            
            if(step == 2 and self.phases == 3): 
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.phases[step+1]))  # 3 si phase == 3

            
            if(self.phases != 3 or step < 4):
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.phases[step]))    # 0, 1, 2 o 3 si phases == 4 

        #priority_phases = {"GrGr": 0, "rGrG": 2, "yryr": 1, "ryry": 3}
        priority_phases = {"GGggrrrrGGggrrrr": 0, "rrrrGGggrrrrGGgg":2, "yyyyrrrryyyyrrrr":1, "rrrryyyyrrrryyyy":3}
        for key in tl_dict:
            tl_dict[key].sort(key=lambda x: priority_phases[x.state])
            traci.trafficlight.setProgramLogic(key, traci.trafficlight.Logic(key, 0, 0, tl_dict[key]))

        y = SUMO.run_simulation(self.simulationSteps)
        SUMO.end_simulation()
        if(self.show_lights): LightsFunctions.__print_lights(tl_dict)
        return 1 - y

    # Recibe los tiempos y configura los semáforos en base a calles en lugar de aleatoriamente (Luego veo XD)
    def coordinated_light(self, x):
        pass




# Por si quieres correr una simulación senshilla
def probar():
    SUMO = SumoSimulation("assets/simulation.sumocfg")

    #SUMO.generate_files("assets/nodes.nod.xml", "assets/edges.edg.xml", "assets/randomTrips.py")
    SUMO.start_simulation(False) 
    
    ended = SUMO.run_simulation(250)
    SUMO.end_simulation()

    return ended

# Por si quieres ver como se pasan las xs a los semáforos
def ejemplo_semaforo():
    #Primero número que semáforo, segundo que etapa
    unaColores = [11, 21, 31, 41] #True, 1
    dosColores = [11, 21, 31, 41, 12, 22, 32, 42] #True, 2
    treColores = [11, 21, 31, 41, 12, 22, 32, 42, 13, 23, 33, 43] #True, 3
    cuaColores = [11, 21, 31, 41, 12, 22, 32, 42, 13, 23, 33, 43, 14, 24, 34, 44] #True, 4
    unaSemafor = [11, 21, 31, 41] #False, 1
    dosSemafor = [11, 12, 21, 22, 31, 32, 41, 42] #False, 2
    treSemafor = [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43] #False, 3
    cuaSemafor = [11, 12, 13, 14, 21, 22, 23, 24, 31, 32, 33, 34, 41, 42, 43, 44] #False, 4

    LF = LightsFunctions(250, False, 4, True)  #250 ciclos, Colores juntos, 2 tiempos
    y = LF.all_lights(cuaSemafor)


def ejemplo_opti():
    LF = LightsFunctions(100, True, 3)  #
    max = [90, 90, 90, 90, 90, 90, 90, 90, 20, 20, 20, 20]
    min = [15, 15, 15, 15, 15, 15, 15, 15, 0, 0, 0, 0]
    x1, y1 = optimization.randomMin(LF.all_lights, min, max, 10)
    x2, y2 = optimization.hill_simulation(LF.all_lights, min, max, 10)
    s = optimization.swarm_simulation(LF.all_lights, min, max, 2, 5)


    print(probar())
    print(y1)
    print(y2)
    print(s.BestY)



if __name__ == "__main__":
    #probar()
    #ejemplo_semaforo()
    ejemplo_opti()
    pass

    
    

    
