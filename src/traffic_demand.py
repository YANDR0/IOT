
from random import randint, choice

def match_traffic(traffic_1: dict, traffic_2: dict):
    in_sum = sum(traffic_1.values())
    out_sum = sum(traffic_2.values())
    diff = in_sum - out_sum

    to_change = traffic_1 if diff > 0 else traffic_2
    diff = abs(diff)

    while(diff) > 0:
        pass
    ### Ya no supe, jaja


def traffic_demand(incoming_traffic: dict, outgoing_traffic: dict):
    #match_traffic(incoming_traffic, outgoing_traffic)
    print()

    traffic = []
    in_sum = sum(incoming_traffic.values())
    proportions = { id: cars/in_sum for id, cars in outgoing_traffic.items() }
    
    leftovers = 0
    for i, total in incoming_traffic.items():
        for j, ratio in proportions.items():
            n = total*ratio-leftovers
            cars = round(n)
            leftovers = cars - n
            traffic.append((i, j, cars))

    return traffic




#def random_traffic_demand(incoming_traffic: dict, outgoing_traffic: dict):


a = {'a': 10, 'b': 10, 'c': 20}
b = {'d': 15, 'e': 17, 'f': 8}

c = traffic_demand(a, b)
for i in c:
    print(i)
