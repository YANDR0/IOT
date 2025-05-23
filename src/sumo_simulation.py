import subprocess
import traci
from os import path
from enum import Enum
#print(os.path.basename(your_path))

class SimulationState(Enum):
    CANNOT_START = 0
    CAN_START = 1
    CAN_RUN = 2
    RUNNING = 3


class SumoSimulation:

    @staticmethod
    def net_from_nod_edg(nodes, edges, dest):
        if('.' not in path.basename(dest)): 
            dest = path.join(dest, "network.net.xml")
        command = f"netconvert -n {nodes} -e {edges} -o {dest}"
        subprocess.run(command.split())
        return dest

    @staticmethod
    def net_from_osm(open_street, dest):
        if('.' not in path.basename(dest)): 
            dest = path.join(dest, "network.net.xml")
        command = f"netconvert --osm-files {open_street} -o {dest}"
        subprocess.run(command.split())
        return dest

    @staticmethod
    def trip_from_od(taz, matrix, dest):
        if('.' not in path.basename(dest)): 
            dest = path.join(dest, "traffic.trips.xml")
        command = f"od2trips -n {taz} -d {matrix} -o {dest}"
        subprocess.run(command.split())
        return dest

    @staticmethod
    def random_trips(network, random, dest):
        if('.' not in path.basename(dest)): 
            dest = path.join(dest, "traffic.trips.xml")
        comando = f"python {random} -n {network} -o {dest} --fringe-factor 50"
        subprocess.run(comando.split())
        return dest

    @staticmethod
    def rou_from_trip(network, trips, dest):
        if('.' not in path.basename(dest)): 
            dest = path.join(dest, "routes.rou.xml")
        command = f"duarouter -n {network} -t {trips} -o {dest}"
        subprocess.run(command.split())
        return dest

    @staticmethod
    def config_from_net_rou(network, routes, dest):
        if('.' not in path.basename(dest)): 
            dest = path.join(dest, "simulation.sumocfg")
        config = f"""
        <configuration>
            <input>
                <net-file value="{network}"/>
                <route-files value="{routes}"/>
            </input>
        </configuration>
        """
        with open(dest, "w") as f: f.write(config)
        return dest
        

    def __init__(self, configuration: str = ""):
        self.sumo_configuration = configuration

        self.step = (
            SimulationState.CAN_START
            if path.exists(configuration)
            else SimulationState.CANNOT_START
        )

    def set_files(self, config) -> None:
        self.sumo_configuration = config
        self.step = SimulationState.CAN_RUN

    def start_simulation(self, visual: bool) -> None:
        if self.step.value < SimulationState.CAN_START.value:
            return

        cmd = ["sumo-gui" if visual else "sumo", "-c", self.sumo_configuration, "--no-warnings"]
        traci.start(cmd)
        self.step = SimulationState.CAN_RUN

    def run_simulation(self, steps: int) -> dict[str, float]:
        if self.step.value < SimulationState.CAN_RUN.value:
            return {}

        self.step = SimulationState.RUNNING

        arrived_number = 0
        departed_number = 0
        average_speed = 0
        average_wait_time = 0
        average_travel_time = 0
        travel_time = {}
        wait_time = {}
        vehicle_speed = {}

        for _ in range(steps):
            traci.simulationStep()
            simulation_time = traci.simulation.getTime()
            departed_number += traci.simulation.getDepartedNumber()

            vehicles = traci.vehicle.getIDList()
            for v in vehicles:
                if(v not in travel_time):
                    travel_time[v] = simulation_time
                    vehicle_speed[v] = []
                    wait_time[v] = 0

                curr_speed = traci.vehicle.getSpeed(v)
                vehicle_speed[v].append(curr_speed)
                wait_time[v] += 1 if curr_speed < 0.1 else 0

            arrived_list = traci.simulation.getArrivedIDList()
            arrived_number += len(arrived_list)
            for arrived in arrived_list:
                travel_time[v] = simulation_time - travel_time[v]

        for v in travel_time:
            average_speed += sum(vehicle_speed[v]) / len(vehicle_speed[v]) if len(vehicle_speed[v]) > 0 else 0
            average_wait_time += wait_time[v]
            average_travel_time += travel_time[v]

        return {
            "arrived_number": arrived_number,
            "departed_number": departed_number,
            "average_speed": average_speed / departed_number if departed_number > 0 else 0,
            "average_wait_time": average_wait_time / departed_number if departed_number > 0 else 0,
            "average_travel_time": average_travel_time / arrived_number if arrived_number > 0 else 0
        }

    def end_simulation(self) -> None:
        if self.step.value < SimulationState.RUNNING.value:
            return
        traci.close()
        self.step = SimulationState.CAN_START

    def get_lights(self):
        if self.step.value < SimulationState.RUNNING.value:
            return
        
        trafficlight_ids = traci.trafficlight.getIDList()
        tl_dict = {}
        total_phases = 0
        for tl in trafficlight_ids:
            logic = traci.trafficlight.getAllProgramLogics(tl)[0]
            tl_dict[tl] = [p.state for p in logic.phases]
            total_phases += len(tl_dict[tl])

        return tl_dict, total_phases

        