import subprocess
import traci

def generateFiles():
    CMDNetwork = '''
    netconvert --node-files=assets/nodes.nod.xml --edge-files=assets/edges.edg.xml --output-file=assets/network.net.xml
    '''.split()

    CMDTrips = "python assets/randomTrips.py -n assets/network.net.xml -o assets/traffic.trips.xml --fringe-factor 50"
    CMDTraffic = "duarouter -n assets/network.net.xml -t assets/traffic.trips.xml -o assets/traffic.rou.xml"

    subprocess.run(CMDNetwork)
    subprocess.run(CMDTrips)
    subprocess.run(CMDTraffic)
    

if __name__ == "__main__":
    generateFiles()

    cmd = ["sumo-gui", "-c", "assets/simulation.sumocfg"]
    traci.start(cmd)

    for step in range(100):
        traci.simulationStep()
    
    traci.close()

    
