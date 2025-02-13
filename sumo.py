import subprocess
import traci
import optimization
from os import path


class SumoSimulation():

    CANNOT_START = 0
    CAN_START = 1
    CAN_RUN = 2

    def __init__(self, configuration):
        self.sumoConfiguration = configuration
        self.step = SumoSimulation.CAN_START if path.exists(self.sumoConfiguration) else SumoSimulation.CANNOT_START

    def generate_files(self, nodes, edges, random):
        CMDNetwork = f"netconvert --node-files {nodes} --edge-files {edges} --tls.guess true --output-file=assets/network.net.xml".split()
        CMDTrips = f"python {random} -n assets/network.net.xml -o assets/traffic.trips.xml --fringe-factor 50"
        CMDTraffic = "duarouter -n assets/network.net.xml -t assets/traffic.trips.xml -o assets/traffic.rou.xml"

        subprocess.run(CMDNetwork)
        subprocess.run(CMDTrips)
        subprocess.run(CMDTraffic)
        self.step = SumoSimulation.CAN_RUN

    def start_simulation(self, visual):
        if(self.step < SumoSimulation.CAN_START): return
        cmd = ["sumo-gui" if visual else "sumo", "-c", self.sumoConfiguration]
        traci.start(cmd)
        self.step = SumoSimulation.CAN_RUN

    def run_simulation(self, steps):
        if(self.step < SumoSimulation.CAN_RUN): return
        
        totalEnds = 0
        totalStarts = 0
        for _ in range(steps):
            traci.simulationStep()
            totalEnds += traci.simulation.getArrivedNumber()
            totalStarts  += traci.simulation.getDepartedNumber()

        traci.close()

        return totalEnds/totalStarts
    
    def end_simulation(self):
        traci.close()
        self.step = SumoSimulation.CAN_START
        
class LightsFunctions():

    def __init__(self):
        self.colorToguether = True
        self.phases = 2

    @staticmethod
    # x es la lista con los tiempos de todos los semáforos, las opciones son: 
    # Todos los verdes, rojos y amarillos juntos, 1r, 2r, 3r...
    # Todo lo de un semáforo junto, verde, rojo, amarillo, verde, rojo, amarillo, ...
    # O si permitir de 2 a 4, ocupo funciones distintas lastimosamente
    def all_lights(x):      
        SUMO = SumoSimulation("assets/simulation.sumocfg")
        SUMO.start_simulation(False)

        tl = traci.trafficlight.getIDList()
        for i in range(len(x)):
            pass
            #phases

        '''
        phases_sem1 = [traci.trafficlight.Phase(20, "GrGr"),  
            traci.trafficlight.Phase(5, "yryr"),   
            traci.trafficlight.Phase(20, "rGrG"),  
            traci.trafficlight.Phase(5, "ryry")]

        traci.trafficlight.setProgramLogic("sem1", traci.trafficlight.Logic("prog1", 0, 0, phases_sem1))
        '''


def probar():
    SUMO = SumoSimulation("assets/simulation.sumocfg")

    #SUMO.generate_files("assets/nodes.nod.xml", "assets/edges.edg.xml", "assets/randomTrips.py")
    SUMO.start_simulation(False) 

    ended = SUMO.run_simulation(250)
    print(ended)

if __name__ == "__main__":
    probar()
    

    
