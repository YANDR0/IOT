import subprocess
import traci
from os import path
from enum import Enum
from convert_field_data import convert_field_data


class SimulationState(Enum):
    CANNOT_START = 0
    CAN_START = 1
    CAN_RUN = 2
    RUNNING = 3


class SumoSimulation:
    def __init__(self, configuration: str, turn_data: str = None):
        self.sumo_configuration = configuration
        self.turn_data = turn_data

        self.step = (
            SimulationState.CAN_START
            if path.exists(configuration)
            else SimulationState.CANNOT_START
        )

    def generate_files(self, nodes: str, edges: str, random: str) -> None:
        # Convertir datos de campo si existen
        if self.turn_data:
            convert_field_data(self.turn_data, './assets/turn_definitions.add.xml')
        
        comando = f"python {random} -n ./assets/network.net.xml -o ./assets/traffic.trips.xml"
        if self.turn_data:
            comando += " --turns ./assets/turn_definitions.add.xml"
        comando += " --fringe-factor 50"
        
        subprocess.run(comando.split())
        self.step = SimulationState.CAN_RUN

    def start_simulation(self, visual: bool) -> None:
        if self.step.value < SimulationState.CAN_START.value:
            return

        cmd = ["sumo-gui" if visual else "sumo", "-c", self.sumo_configuration]
        traci.start(cmd)
        self.step = SimulationState.CAN_RUN

    def run_simulation(self, steps: int) -> dict[str, float]:
        if self.step.value < SimulationState.CAN_RUN.value:
            return {}

        self.step = SimulationState.RUNNING
        total_ends, total_starts, total_wait_time, total_speed, total_vehicles = (
            0,
            0,
            0,
            0,
            0,
        )

        for _ in range(steps):
            traci.simulationStep()
            total_ends += traci.simulation.getArrivedNumber()
            total_starts += traci.simulation.getDepartedNumber()
            vehicles = traci.vehicle.getIDList()
            total_vehicles += len(vehicles)

            for vehicle in vehicles:
                total_wait_time += traci.vehicle.getAccumulatedWaitingTime(vehicle)
                total_speed += traci.vehicle.getSpeed(vehicle)

        return {
            "traffic_flow": total_ends / total_starts if total_starts else 0.0,
            "avg_wait_time": total_wait_time / total_vehicles
            if total_vehicles
            else 0.0,
            "avg_speed": total_speed / total_vehicles if total_vehicles else 0.0,
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

        