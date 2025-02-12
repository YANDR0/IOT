import subprocess
import traci

class SumoSimulation():
    def __init__(self):
        pass


def generateFiles():
    CMDNetwork = '''
    netconvert --node-files assets/nodes.nod.xml --edge-files assets/edges.edg.xml --tls.guess true --output-file=assets/network.net.xml
    '''.split()

    CMDTrips = "python assets/randomTrips.py -n assets/network.net.xml -o assets/traffic.trips.xml --fringe-factor 50"
    CMDTraffic = "duarouter -n assets/network.net.xml -t assets/traffic.trips.xml -o assets/traffic.rou.xml"

    subprocess.run(CMDNetwork)
    subprocess.run(CMDTrips)
    subprocess.run(CMDTraffic)


    
def runSimulation(steps):
    cmd = ["sumo", "-c", "assets/simulation.sumocfg"]
    #cmd = ["sumo-gui", "-c", "assets/simulation.sumocfg"]

    traci.start(cmd)
    #Pongo acá los semáforos mejor, también como argumento creo
    
    totalEnds = 0
    for _ in range(steps):
        traci.simulationStep()
        lights = traci.trafficlight.getIDList()
        ended = traci.simulation.getArrivedIDList()
        totalEnds += len(ended)
    traci.close()

    return totalEnds, lights



if __name__ == "__main__":

    a,b = runSimulation(500)    #860 es el limite exclusivo que aguanta la simulación  
    
    print(f"Arrives = {a}")
    print(b)

    
