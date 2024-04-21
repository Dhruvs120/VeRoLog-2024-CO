import itertools
from gurobipy import Model, GRB, quicksum

tools_model = Model("Tools")

file_path = '/Users/stelianmunteanu/Desktop/univer/Combinatorial Optimization/Case/validator/CO_Case2420sol.txt' # Specify the path and filename
instance_file = "instances 2024/CO_Case2401.txt" # Replace with your actual file path

usable_name = file_path.split('/')[-1].split('.')[0]  # Extract the name of the file without the extension

def start_location(locations,start_location_id):
    for location in locations.values():
        if location.id == start_location_id:
            return location
    
def distance(point1, point2):
    return ((point1.x - point2.x)**2 + (point1.y - point2.y)**2) ** 0.5

def find_routes(start_location_id, max_distance,locations):
    # Filter locations to include only those with ID not equal to start_location_id
    destinations = []
    for loc in locations.values():
        if loc.id != start_location_id:
            destinations.append(loc)
    routes = []
    

    # Generate all possible permutations of destinations
    for r in range(1, len(destinations) + 1):
        for perm in itertools.permutations(destinations, r):
            route = [start_location(locations, start_location_id)] + list(perm) + [start_location(locations, start_location_id)]
            total_distance = sum(distance(route[i], route[i+1]) for i in range(0,len(route)-1))
            if total_distance <= max_distance:
                routes.append([route,total_distance])
    return routes

def possible_schedules(dataset):
    
    days = []
    for i in range(1,dataset.days+1):
        days.append(i)
    
    schedules = []
    for r in range(1, dataset.days+1):
        for perm in itertools.permutations(days,r):
            if all(perm[i] < perm[i+1] for i in range(len(perm)-1)):
                consecutive_days = False
                for i in range(len(perm)-4):
                    if perm[i+4] - perm[i] == 4:
                        consecutive_days = True
                        break
                if not consecutive_days:
                    schedules.append(list(perm))
    return schedules

def Optimize(dataset, machines, locations, requests,technicians ): 
    truck_routes = find_routes('1', dataset.truck_max_distance,locations)
    
    technician_routes = []
    for technician in technicians.values():
        routes = find_routes(technician.location_id, 10000000, locations)
        technician_routes.extend(routes)
    
    schedules = possible_schedules(dataset)
    
    #Xr_d
    route_each_day = {}
    for day in range(1,dataset.days+1):
        route_each_day[day] = {}
        for i in range(0,len(truck_routes)):
            route_each_day[day][i] = tools_model.addVar(vtype = GRB.BINARY)
    
    #N_trucks
    number_of_trucks = tools_model.addVar(vtype=GRB.INTEGER)
    
    #y_p_t,d
    technician_tour_day = {}
    for technician in range(0,len(technicians)):
        technician_tour_day[technician] = {}
        for day in range(1,dataset.days +1):
            technician_tour_day[technician][day] = {}
            for route in range(0,len(technician_routes)):
                if technician_routes[route][0][0].id == technicians[technician+1].location_id:
                    technician_tour_day[technician][day][route] = tools_model.addVar(vtype=GRB.BINARY)
                else:
                    technician_tour_day[technician][day][route] = 0
                    
    #request_on_route_and_day = {}
    #for request in range(1,len(requests)+1):
        #request_on_route_and_day[request] = {}
        #for route in range(0,len(truck_routes)):
            #request_on_route_and_day[request][route] = {}
            #for day in range(1,dataset.days+1):
                #request_on_route_and_day[request][route][day] = tools_model.addVar(vtype=GRB.BINARY)
    
    #capacity_each_request = {}
    #quantity_each_request = {}
    #for request in range(1,len(requests)+1):
        #capacity_each_request[request] = machines[requests[request].machine_id].size
        #quantity_each_request[request] = requests[request].quantity
        
    #z_ps
    technician_schedule = {}
    for technician in range(0,len(technicians)):
        technician_schedule[technician] = {}
        for schedule in range(0,len(schedules)):
            technician_schedule[technician][schedule] = tools_model.addVar(vtype= GRB.BINARY)
    
    #b_t,m
    request_is_in_tecnician_route = {}
    for route in range(0,len(technician_routes)):
        request_is_in_tecnician_route[route] = {}
        for request in range(1,len(requests)+1):
            request_is_in_tecnician_route[route][request] = 0
            for i in range(0,len(technician_routes[route][0])):
                if requests.get(request).location_id == technician_routes[route][0][i].id:
                    request_is_in_tecnician_route[route][request] = 1

    #A_rm
    request_is_in_truck_route = {}
    for route in range(0,len(truck_routes)):
        request_is_in_truck_route[route] = {}
        for i in range(1,len(requests)+1):
            request_is_in_truck_route[route][i] = 0
            for j in range(0,len(truck_routes[route][0])):
                if requests.get(i).location_id == truck_routes[route][0][j].id:
                    request_is_in_truck_route[route][i] = 1
            
    #C_r
    truck_cost_each_route = {}
    for i in range(0,len(truck_routes)):
        truck_cost_each_route[i] = dataset.truck_day_cost + (truck_routes[i][1]*dataset.truck_distance_cost)
        
    #e_s,d
    schedule_has_certain_day = {}
    for schedule in range(0,len(schedules)):
        schedule_has_certain_day[schedule] = {}
        for day in range(0,dataset.days+1):
            schedule_has_certain_day[schedule][day] = 0
            for i in range(0,len(schedules[schedule])):
                if day == schedules[schedule][i]:
                    schedule_has_certain_day[schedule][day] = 1
     
    #h_t_p
    technician_cost_per_tour = {}
    for technician in range(0,len(technicians)):
        technician_cost_per_tour[technician] = {}
        for route in range(0,len(technician_routes)):
            technician_cost_per_tour[technician][route] = 1000000
            if technician_routes[route][0][0].id == technicians[technician+1].location_id:
                technician_cost_per_tour[technician][route] = dataset.technician_day_cost + dataset.technician_distance_cost*technician_routes[route][1]
                
    
    #W_m
    idle_days_request = {}
    for request in range(1,len(requests)+1):
        last_day = quicksum(day*request_is_in_tecnician_route[route][request]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,dataset.days +1))
        first_day = quicksum(day*request_is_in_truck_route[route][request]*route_each_day[day][route] for day in range(1,dataset.days+1) for route in range(0,len(truck_routes)))
        idle_days_request[request] = last_day - first_day
            
    #C_m
    request_idle_cost = {}
    for request in range(1,len(requests)+1):
        request_idle_cost[request] = machines.get(requests.get(request).machine_id).idle_penalty
    
    #trying
    #for route in range(0,len(truck_routes)):
        #for day in range(1,dataset.days+1):
            #tools_model.addConstr(quicksum(capacity_each_request[request]*quantity_each_request[request]*request_on_route_and_day[request][route][day] for request in range(1,len(requests)+1) ) <= dataset.truck_capacity)
    
    #trying
    #for request in range(1,len(requests)+1):
        #tools_model.addConstr(quicksum(request_on_route_and_day[request][route][day] for day in range(1,dataset.days+1) for route in range(0,len(truck_routes))) == 1)
    
    for day in range(1,dataset.days+1):
        tools_model.addConstr(quicksum(route_each_day[day][i] for i in range(0,len(truck_routes))) <= number_of_trucks)
    
    for request in range(1,len(requests)+1):
        tools_model.addConstr(quicksum(request_is_in_truck_route[route][request]*route_each_day[day][route] for route in range(0,len(truck_routes)) for day in range(1,dataset.days+1)) == 1)
    
        
    for technician in range(0,len(technicians)):
        tools_model.addConstr(quicksum(technician_schedule[technician][schedule] for schedule in range(0,len(schedules)) ) <= 1)
    
    for technician in range(0,len(technicians)):
        for day in range(1,dataset.days+1):
            tools_model.addConstr(quicksum(technician_tour_day[technician][day][route] for route in range(0,len(technician_routes)))<= quicksum(schedule_has_certain_day[schedule][day]*technician_schedule[technician][schedule]for schedule in range(0,len(schedules))))
            #tools_model.addConstr( quicksum(schedule_has_certain_day[schedule][day]*technician_schedule[technician][schedule]for schedule in range(0,len(schedules))) == 1)
    
    for request in range(1,len(requests)+1):
        tools_model.addConstr( quicksum(request_is_in_tecnician_route[route][request]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,dataset.days +1) )== 1)
    
    for day in range(1,dataset.days+1):
        for request in range(1,len(requests)+1):
            tools_model.addConstr(quicksum(request_is_in_tecnician_route[route][request]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) ) <= quicksum(request_is_in_truck_route[route][request]*route_each_day[day][route] for day in range(1,dataset.days) for route in range(0,len(truck_routes))))
    
    #trying
    #for day in range(1,dataset.days+1):
        #for route in range(0,len(truck_routes)):
            #tools_model.addConstr( route_each_day[day][route] == quicksum(request_on_route_and_day[request][route][day] for request in range(1,len(requests)+1)))
    
    
    for request in range(1,len(requests)+1):
        tools_model.addConstr(idle_days_request[request] >= 0)
    #tools_model.setObjective(quicksum(truck_cost_each_route[i] * quicksum(route_each_day[day][i] for day in range(1,dataset.days+1) ) for i in range(0,len(truck_routes))),GRB.MINIMIZE)
    #tools_model.setObjective(number_of_trucks*dataset.truck_cost,GRB.MINIMIZE)
    #tools_model.setObjective(quicksum(request_idle_cost[request]*idle_days_request[request] for request in range(1,len(requests)+1)),GRB.MINIMIZE)
    #tools_model.setObjective(quicksum(technician_cost_per_tour[technician][route]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,dataset.days +1)),GRB.MINIMIZE)
    tools_model.setObjective((dataset.technician_cost * quicksum(technician_schedule[technician][schedule] for technician in range (0,len(technicians)) for schedule in range(0,len(schedules))))+(number_of_trucks*dataset.truck_cost)+(quicksum(truck_cost_each_route[i] * quicksum(route_each_day[day][i] for day in range(1,dataset.days+1) ) for i in range(0,len(truck_routes))))+(quicksum(request_idle_cost[request]*idle_days_request[request] for request in range(1,len(requests)+1))) + (quicksum(technician_cost_per_tour[technician][route]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,dataset.days +1))), GRB.MINIMIZE)
    tools_model.optimize()
    
    #for request in range(1,len(requests)+1):
        #for day in range(1,dataset.days+1):
            #for route in range(0,len(truck_routes)):
                #if request_on_route_and_day[request][route][day].x ==1:
                    #print("request:", request, "day:",day)
    print(number_of_trucks)
    
    total_truck_distance = 0
    total_trucks_used = 0
    max_trucks_used = 0
    for day in range(1,dataset.days+1):
        for i in range(0,len(truck_routes)):

            if len(route_each_day[day]) > max_trucks_used:
                max_trucks_used = len(route_each_day[day])

            if route_each_day[day][i].X == 1.0:
                total_truck_distance = total_truck_distance + truck_routes[i][1]
                total_trucks_used += 1

    total_technician_distance = 0
    total_technicians_used = 0
    technician_per_day = {day : 0 for day in range(1, dataset.days+1)}

    for technician in range(0, len(technicians)):
        for day in range(1, dataset.days+1):
            for route in range(0, len(technician_routes)):
                if technician_tour_day[technician][day][route].X == 1.0:
                    technician_per_day[day] += 1
                    total_technician_distance += technician_routes[route][1]
                    total_technicians_used += 1
    

    with open(file_path, 'w') as results:
        results.writelines([
            f"\nDATASET =  {dataset}", 
            f"NAME = {usable_name}", 
            f"\nTRUCK_DISTANCE = {round(total_truck_distance)}",   
            f"\nNUMBER_OF_TRUCK_DAYS = {total_trucks_used}", 
            f"\nNUMBER_OF_TRUCKS_USED = {max_trucks_used}", 
            f"\nTECHNICIAN_DISTANCE = {round(total_technician_distance)}", 
            f"\nNUMBER_OF_TECHNICIAN_DAYS = {total_technicians_used}", 
            f"\nNUMBER_OF_TECHNICIANS_USED = {max(technician_per_day.values())}", 
            f"\nIDLE_MACHINE_COSTS = {sum(request_idle_cost.values())}", 
            f"\nTOTAL_COST = {round(tools_model.objVal)}\n" 
        ])

# Still need to work this part out, doesn't look too difficult though  
    #     for i in range(1, days + 1): 
    #         number_of_trucks = 0
    #         if route_schedule[i][0]:
    #             number_of_trucks = len(route_schedule[i])
                
    #         results.writelines([
    #         f"\nDAY = {i}",     
    #         f"\nNUMBER_OF_TRUCKS = {number_of_trucks}"])
            
    #         for truck_id in range(number_of_trucks):
    #             results.writelines([
    #                 f"\n {truck_id + 1} {' '.join(map(str, route_schedule[i][truck_id]))}"])
            
    #         results.writelines([f"\nNUMBER_OF_TECHNICIANS = {len(tech_schedule[i])}"])
    #         for route, technician_id in tech_schedule[i].items():
    #             results.writelines([
    #                 f"\n {technician_id} {' '.join(map(str, route))}"])



class Dataset:
    def __init__(self, name):
        self.name = name
        self.days = None
        self.truck_capacity = None
        self.truck_max_distance = None
        self.truck_distance_cost = None
        self.truck_day_cost = None
        self.truck_cost = None
        self.technician_distance_cost = None
        self.technician_day_cost = None
        self.technician_cost = None


class Machine:
    def __init__(self, id, size, idle_penalty):
        self.id = id
        self.size = size
        self.idle_penalty = idle_penalty


class Location:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y


class Request:
    def __init__(self, id, location_id, start_day, end_day, machine_id, quantity):
        self.id = id
        self.location_id = location_id
        self.start_day = start_day
        self.end_day = end_day
        self.machine_id = machine_id
        self.quantity = quantity


class Technician:
    def __init__(self, id, location_id, max_distance_per_day, max_installations_per_day, machine_capabilities):
        self.id = id
        self.location_id = location_id
        self.max_distance_per_day = max_distance_per_day
        self.max_installations_per_day = max_installations_per_day
        self.machine_capabilities = machine_capabilities


def ReadInstance(instance_file):
    dataset = None
    machines = {}
    locations = {}
    requests = {}
    technicians = {}

    with open(instance_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                key, *values = line.split()
                if key == 'DATASET':
                    dataset_name = line.split('=')[-1].strip()
                    dataset = Dataset(dataset_name)
                elif key == 'NAME':
                    dataset.name = ' '.join(values[1:])
                elif key == 'DAYS':
                    dataset.days = int(values[-1])
                elif key == 'TRUCK_CAPACITY':
                    dataset.truck_capacity = int(values[-1])
                elif key == 'TRUCK_MAX_DISTANCE':
                    dataset.truck_max_distance = int(values[-1])
                elif key == 'TRUCK_DISTANCE_COST':
                    dataset.truck_distance_cost = int(values[-1])
                elif key == 'TRUCK_DAY_COST':
                    dataset.truck_day_cost = int(values[-1])
                elif key == 'TRUCK_COST':
                    dataset.truck_cost = int(values[-1])
                elif key == 'TECHNICIAN_DISTANCE_COST':
                    dataset.technician_distance_cost = int(values[-1])
                elif key == 'TECHNICIAN_DAY_COST':
                    dataset.technician_day_cost = int(values[-1])
                elif key == 'TECHNICIAN_COST':
                    dataset.technician_cost = int(values[-1])

                elif key == 'MACHINES':
                    num_machines_line = line.strip()
                    num_machines = int(num_machines_line.split('=')[-1].strip().split()[0])
                    for _ in range(num_machines):
                        machine_line = file.readline().strip()
                        if machine_line:
                            machine_values = machine_line.split()
                            if len(machine_values) == 3:
                                machine_id = machine_values[0]
                                size = int(machine_values[1])
                                idle_penalty = int(machine_values[2])
                                machines[machine_id] = Machine(machine_id, size, idle_penalty)
                            else:
                                print("Error: Invalid format in MACHINES section.")
                        else:
                            print("Error: Expected number of machines not found in MACHINES section.")
                elif key == 'LOCATIONS':
                    num_locations_line = line.strip()
                    num_locations = int(num_locations_line.split('=')[-1].strip().split()[0])
                    for _ in range(num_locations):
                        location_line = file.readline().strip()
                        if location_line:
                            location_values = location_line.split()
                            if len(location_values) == 3:
                                location_id = location_values[0]
                                x = int(location_values[1])
                                y = int(location_values[2])
                                locations[location_id] = Location(location_id, x, y)
                            else:
                                print("Error: Invalid format in LOCATIONS section.")
                        else:
                            print("Error: Expected number of locations not found in LOCATIONS section.")
                elif key == 'REQUESTS':
                    num_requests_line = line.strip()
                    num_requests = int(num_requests_line.split('=')[-1].strip())
                    for _ in range(num_requests):
                        request_line = file.readline().strip()
                        if request_line:
                            request_values = request_line.split()
                            if len(request_values) == 6:
                                request_id = int(request_values[0])
                                location_id = request_values[1]
                                start_day = int(request_values[2])
                                end_day = int(request_values[3])
                                machine_id = request_values[4]
                                quantity = int(request_values[5])
                                requests[request_id] = Request(request_id, location_id, start_day, end_day, machine_id, quantity)
                            else:
                                print("Error: Invalid format in REQUESTS section.")
                        else:
                            print("Error: Expected number of requests not found in REQUESTS section.")
                elif key == 'TECHNICIANS':
                    num_technicians_line = line.strip()
                    num_technicians = int(num_technicians_line.split('=')[-1].strip())
                    for _ in range(num_technicians):
                        technician_line = file.readline().strip()
                        if technician_line:
                            technician_values = technician_line.split()
                            if len(technician_values) >= 5:
                                technician_id = int(technician_values[0])
                                location_id = technician_values[1]
                                max_distance_per_day = int(technician_values[2])
                                max_installations_per_day = int(technician_values[3])
                                machine_capabilities = [int(val) for val in technician_values[4:]]
                                technicians[technician_id] = Technician(technician_id, location_id, max_distance_per_day, max_installations_per_day, machine_capabilities)
                            else:
                                print("Error: Invalid format in TECHNICIANS section.")
                        else:
                            print("Error: Expected number of technicians not found in TECHNICIANS section.")

    return dataset, machines, locations, requests, technicians


if __name__ == "__main__":
    dataset, machines, locations, requests, technicians = ReadInstance(instance_file)

    # Sanity check
    print("Dataset:")
    print(dataset.__dict__)

    print("\nMachines:")
    for machine in machines.values():
        print(machine.__dict__)

    print("\nLocations:")
    for location in locations.values():
        print(location.__dict__)

    print("\nRequests:")
    for request in requests.values():
        print(request.__dict__)

    print("\nTechnicians:")
    for technician in technicians.values():
        print(technician.__dict__)
    print("begin:")
    Optimize(dataset, machines, locations, requests, technicians)
    # Return a specific technician's attribute based on their id    
    # print(technicians.get(1).machine_capabilities)
