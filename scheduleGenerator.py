import itertools

def possible_schedules(dataset, requests, machines):
    days = []
    schedules = []
    max_capacity = dataset.truck_capacity
    
    machine_weights = {machine.id: machine.size for machine in machines.values()}

    for i in range(1,dataset.days+1):
        days.append(i)
    
    for r in range(1, dataset.days+1):
        for perm in itertools.permutations(days,r):
            if all(perm[i] < perm[i+1] for i in range(len(perm)-1)):
                consecutive_days = False
                for i in range(len(perm)-4):
                    if perm[i+4] - perm[i] == 4:
                        consecutive_days = True
                        break
                if not consecutive_days:
                    sum_weight = 0
                    for i in range(len(perm)):
                        sum_weight += machine_weights[requests[i].machine_id] * requests[i].quantity
                    if sum_weight <= max_capacity:
                        schedules.append(list(perm))
    return schedules