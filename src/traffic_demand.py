
from random import randint
from os import path

class TrafficDemand:

    @staticmethod
    def match_traffic(traffic_1: dict, traffic_2: dict):
        in_sum = sum(traffic_1.values())
        out_sum = sum(traffic_2.values())
        diff = in_sum - out_sum

        if(diff == 0): return

        traffic_to_change = traffic_1 if diff < 0 else traffic_2
        sum_change = in_sum if diff < 0 else out_sum
        diff = abs(diff)
        initial_diff = diff

        leftovers = 0

        while(diff) > 0:
            for k in traffic_to_change:
                n = initial_diff*(traffic_to_change[k]/sum_change)-leftovers
                cars = round(n)
                leftovers = cars - n
                traffic_to_change[k] += cars
                diff -= cars

    @staticmethod
    def traffic_demand(incoming_traffic: dict, outgoing_traffic: dict):
        TrafficDemand.match_traffic(incoming_traffic, outgoing_traffic)
        traffic = []
        in_sum = sum(incoming_traffic.values())
        
        leftovers = 0
        for i, total_in in incoming_traffic.items():
            for j, total_out in outgoing_traffic.items():
                n = total_in*(total_out/in_sum)-leftovers
                cars = round(n)
                leftovers = cars - n
                traffic.append((i, j, cars))

        return traffic

    @staticmethod
    def random_traffic_demand(incoming_traffic: dict, outgoing_traffic: dict):
        TrafficDemand.match_traffic(incoming_traffic, outgoing_traffic)
        traffic = []
        out_list = [k for k in outgoing_traffic]

        for in_k in incoming_traffic:
            values = dict()

            while(incoming_traffic[in_k] > 0):
                i = randint(0, len(out_list)-1)
                out_key = out_list[i]
                cars = randint(1, min(incoming_traffic[in_k], outgoing_traffic[out_key]))

                incoming_traffic[in_k] -= cars
                outgoing_traffic[out_key] -= cars
                values[out_key] = cars + (values.get(out_key) or 0)

                if(outgoing_traffic[out_key] == 0):
                    out_list[i] = out_list[-1]
                    out_list.pop()
            
            for out_key in values:
                traffic.append((in_k, out_key, values[out_key]))

        return traffic

    @staticmethod
    def write_taz_od(incoming_traffic: dict, outgoing_traffic: dict, traffic, time, dest):
        taz = path.join(dest, "tazes.taz.xml")
        with open(taz, "w") as f:
            f.write("<tazs>\n")
            for k in incoming_traffic:
                f.write(f'\t<taz id="{k}" edges="{k}"/>\n')
            for k in outgoing_traffic:
                f.write(f'\t<taz id="{k}" edges="{k}"/>\n')
            f.write("</tazs>\n")

        od = path.join(dest, "matriz.od")
        with open(od, "w") as f:
            f.write("$OR;D2 \n")
            f.write(time)
            f.write("\n1.00\n")
            for t in traffic:
                f.write(f"{t[0]} {t[1]} {t[2]}")

        return taz, od
                




