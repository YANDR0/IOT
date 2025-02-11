import subprocess
import traci

def generateFiles():
    CMDNetwork = '''
    netconvert --node-files assets/nodes.nod.xml --edge-files assets/edges.edg.xml --tls.guess true --output-file=assets/network.net.xml
    '''.split()

    CMDTrips = "python assets/randomTrips.py -n assets/network.net.xml -o assets/traffic.trips.xml --fringe-factor 50"
    CMDTraffic = "duarouter -n assets/network.net.xml -t assets/traffic.trips.xml -o assets/traffic.rou.xml"

    subprocess.run(CMDNetwork)
    subprocess.run(CMDTrips)
    subprocess.run(CMDTraffic)
    

if __name__ == "__main__":
    #generateFiles()

    cmd = ["sumo", "-c", "assets/simulation.sumocfg"]
    #cmd = ["sumo-gui", "-c", "assets/simulation.sumocfg"]
    traci.start(cmd)

    totalEnds = 0
    for step in range(500):
        traci.simulationStep()
        lights = traci.trafficlight.getIDList()
        ended = traci.simulation.getArrivedIDList()
        totalEnds += len(ended)
    
    traci.close()

    print(f"Arrives = {totalEnds}")

    
