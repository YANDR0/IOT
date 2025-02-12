import subprocess
import traci
from os import path

class SumoSimulation():

    CANNOT_START = 0
    CAN_START = 1
    CAN_RUN = 2

    def __init__(self):
        self.sumoConfiguration = "assets/simulation.sumocfg"
        self.step = SumoSimulation.CAN_START if path.exists("assets/simulation.sumocfg") else SumoSimulation.CANNOT_START

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
        cmd = ["sumo-gui" if visual else "sumo", "-c", "assets/simulation.sumocfg"]
        traci.start(cmd)
        self.step = SumoSimulation.CAN_RUN

    def run_simulation(self, steps):
        if(self.step < SumoSimulation.CAN_RUN): return
        tl = traci.trafficlight.getIDList()
    
        totalEnds = 0
        totalStarts = 0
        for _ in range(steps):
            traci.simulationStep()
            totalEnds += traci.simulation.getArrivedNumber()
            totalStarts  += traci.simulation.getDepartedNumber()

        traci.close()

        return totalEnds, totalStarts, tl
        


if __name__ == "__main__":
    SUMO = SumoSimulation()

    #SUMO.generate_files("assets/nodes.nod.xml", "assets/edges.edg.xml", "assets/randomTrips.py")
    SUMO.start_simulation(False) 
    ends, start, sema = SUMO.run_simulation(250)
    print(ends, start, sema)

    
