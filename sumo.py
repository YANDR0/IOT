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
    phases = ["GrGr", "rGrG", "yryr", "ryry"]

    # Crea administrador de las funciones, steps define los pasos o ciclos de la simulación
    # color si los datos de x están juntos por color y phases cuantos tiempos se dieron (Más detalles en all lights)
    def __init__(self, steps, color, phases):
        self.simulationSteps = steps  #Cantidad de pasos en la simulación
        self.color_toguether = color  #Parámetros están juntos por color o por semáforo
        self.phases = phases     #Cuales ciclos duran igual


    # Recibe los tiempos y configura los semáforos de manera individual en base a eso
    def all_lights(self, x):      
        SUMO = SumoSimulation("assets/simulation.sumocfg")
        SUMO.start_simulation(False)

        tl = traci.trafficlight.getIDList()
        tl_num = len(tl)
        tl_dict = {id:[] for id in tl}
        
        
        for i in range(tl_num*self.phases):
            id = tl[i % tl_num if self.color_toguether else (i-1)//self.phases]

            #Si fase es 1, todos los colores duran lo mismo
            if(self.phases == 1):
                tl_dict[id] = [traci.trafficlight.Phase(x[i], p) for p in LightsFunctions.phases]   # 0, 1, 2 y 3
                continue

            step = len(tl_dict[id])
            #Si fase es 2, rojo y verde duran lo mismo, ambos amarillos duran lo mismo
            if(self.phases == 2):
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.phases[step]))    # 0 o 2  
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.phases[step+1]))  # 1 o 3
                continue

            #Si fase es 3, cada color dura lo suyo, verde, rojo y ambos amarillos
            if(step == 2 and self.phases == 3): 
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.phases[step+1]))  # 3 si phase == 3

            #Si fase es 4, cada etapa dura lo suyo, verde, rojo, amarillo 1, amarillo 2 
            if(self.phases != 3 or step < 4):
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.phases[step]))    # 0, 1, 2 o 3 si phases == 4 

        priority_phases = {"GrGr": 0, "rGrG": 2, "yryr": 1, "ryry": 3}
        for key in tl_dict:
            tl_dict[key].sort(key=lambda x: priority_phases[x.state])
            #traci.trafficlight.setProgramLogic(key, traci.trafficlight.Logic(key, 0, 0, tl_dict[key]))

        SUMO.run_simulation(self.simulationSteps)

        SUMO.end_simulation()
        return tl_dict

    # Recibe los tiempos y configura los semáforos en base a calles en lugar de aleatoriamente (Luego veo XD)
    def coordinated_light(self, x):
        pass

# Por si quieres correr una simulación senshilla
def probar():
    SUMO = SumoSimulation("assets/simulation.sumocfg")

    #SUMO.generate_files("assets/nodes.nod.xml", "assets/edges.edg.xml", "assets/randomTrips.py")
    SUMO.start_simulation(False) 

    ended = SUMO.run_simulation(250)
    
    print(ended)
    SUMO.end_simulation()



if __name__ == "__main__":
    #probar()

    #'''
    LF = LightsFunctions(250, False, 3)  #250 ciclos, Colores juntos, 2 tiempos
    a = [i for i in range(1000)]
    b = LF.all_lights(a)    #X temporal, luego la pongo bien XD

    for i in b:
        print(i, " ", end="")
        for j in b[i]:
            print(j.state, j.duration, end=" ")
        print()
        #'''
    

    
