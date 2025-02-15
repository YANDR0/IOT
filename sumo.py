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

    # Fases del semáforo (La letra dice de que color está)
    phases = ["GrGr", "yryr", "rGrG", "ryry"]

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
        
        for i in range(tl_num*self.phases+1):
            id = tl[i % tl_num if self.color_toguether else (i-1)//self.phases]

            #Si fase es 1, todos los colores duran lo mismo
            if(self.phases == 1):
                tl_dict[id] = [traci.trafficlight.Phase(x[i], p) for p in LightsFunctions.phases]

            #Si fase es 2, rojo y verde duran lo mismo, ambos amarillos duran lo mismo
            if(self.phases == 2):
                step = len(tl_dict[id])//2
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.phases[step]))
                tl_dict[id].append(traci.trafficlight.Phase(x[i], LightsFunctions.phases[step+1]))

            #Si fase es 3, cada color dura lo suyo, verde, rojo y ambos amarillos
            if(self.phases == 3):
                pass

            #Si fase es 4, cada etapa dura lo suyo
            if(self.phases == 4):
                pass

        for key in tl_dict:
            traci.trafficlight.setProgramLogic(key, traci.trafficlight.Logic(key, 0, 0, tl_dict[key]))

        #SUMO.run_simulation(self.simulationSteps)
        SUMO.end_simulation()
        return 0

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

    LF = LightsFunctions(250, True, 2)  #250 ciclos, Colores juntos, 2 tiempos
    LF.all_lights(1)    #X temporal, luego la pongo bien XD
    

    
