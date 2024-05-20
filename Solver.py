import gurobipy as gp
from gurobipy import  GRB, quicksum
from partFunctions import distance
from routeFinder import find_routes
from scheduleGenerator import possible_schedules
from instanceReader import ReadInstance

instance_file = "instances 2024/CO_Case2413.txt" # Replace with your actual file path
solution_file_path = 'instances 2024/CO_Case2413sol.txt' # Specify the path and filename
timelim = 600 # Specify the time limit in seconds

tools_model = gp.Model("Tools")

def Optimize(dataset, machines, locations, requests,technicians, sol_path, time_limit):

    print("0")
    #All possible truck routes
    truck_routes = find_routes('1', dataset.truck_max_distance,locations)
    
    print("1")
    #All possible technician routes
    technician_routes = []
    technicians_id = []
    for technician in technicians.values():
        technician_not_used = True
        for i in range(0,len(technicians_id)):
            if technician.location_id == technicians_id[i]:
                technician_not_used = False
                if technician.max_distance_per_day >= technicians_id[i][1]:
                    technicians_id[i][1] = technician.max_distance_per_day
        if technician_not_used:
            technicians_id.append([technician.location_id,technician.max_distance_per_day])
    
    print(technicians_id)
    
    for i in range(0,len(technicians_id)):
        routes = find_routes(technicians_id[i][0], technicians_id[i][1], locations)
        technician_routes.extend(routes)
            
        
    print("2")
    #All possible schedules for technicians
    schedules = possible_schedules(dataset)
    print("3")
    #Number of trucks used
    
    if len(locations) > 7:
        number_of_trucks = 3
    else:
        number_of_trucks = 2
    
    print(number_of_trucks)

    routes_for_each_truck = {}
    for day in range(1,dataset.days+1):
        routes_for_each_truck[day] = {}
        for truck in range(0,number_of_trucks):
            routes_for_each_truck[day][truck] = {}
            for route in range(0, len(truck_routes)):
                routes_for_each_truck[day][truck][route] = {}
                for request in range(1, len(requests)+1):
                    routes_for_each_truck[day][truck][route][request] = tools_model.addVar(vtype=GRB.BINARY)
                    if day < requests[request].start_day:
                        routes_for_each_truck[day][truck][route][request] = 0
                    if day > requests[request].end_day:
                        routes_for_each_truck[day][truck][route][request] = 0
                    request_is_in_route = False
                    for j in range(0,len(truck_routes[route][0])):
                        if requests[request].location_id == truck_routes[route][0][j].id:
                            request_is_in_route = True
                    if (request_is_in_route == False):
                        routes_for_each_truck[day][truck][route][request] = 0
    
    print("4")
    routes_for_each_technician = {}
    for technician in range(1,len(technicians)+1):
        routes_for_each_technician[technician] = {}
        for day in range(1,dataset.days+1):
            routes_for_each_technician[technician][day] = {}
            for route in range(0,len(technician_routes)):
                routes_for_each_technician[technician][day][route] = {}
                for request in range(1,len(requests)+1):
                    routes_for_each_technician[technician][day][route][request] = tools_model.addVar(vtype=GRB.BINARY)
                    request_is_in_route = False
                    for i in range(0,len(technician_routes[route][0])):
                        if requests[request].location_id == technician_routes[route][0][i].id:
                            request_is_in_route = True
                    if (request_is_in_route == False):
                        routes_for_each_technician[technician][day][route][request] = 0
                    for machine in range(0,len(technicians[technician].machine_capabilities)):
                        if technicians[technician].machine_capabilities[machine] == 0:
                            if (int(requests[request].machine_id)) == (machine+1):
                                routes_for_each_technician[technician][day][route][request] = 0
                    if technicians[technician].location_id != technician_routes[route][0][0].id:
                        routes_for_each_technician[technician][day][route][request] = 0
    print("5")
    route_each_technician_each_day = {}
    for technician in range(1,len(technicians)+1):
        route_each_technician_each_day[technician] = {}
        for day in range(1,dataset.days+1):
            route_each_technician_each_day[technician][day] = {}
            for route in range(0,len(technician_routes)):
                route_each_technician_each_day[technician][day][route] = tools_model.addVar(vtype=GRB.BINARY)
    print("6")
    truck_each_day = {}
    route__each_truck_each_day = {}
    for day in range(1,dataset.days+1):
        truck_each_day[day] = {}
        route__each_truck_each_day[day] = {}
        for truck in range(0,number_of_trucks):
            truck_each_day[day][truck] = tools_model.addVar(vtype=GRB.BINARY)
            route__each_truck_each_day[day][truck] = {}
            for route in range(0, len(truck_routes)):
                route__each_truck_each_day[day][truck][route] = tools_model.addVar(vtype=GRB.BINARY)
    
    print("7")
    #Calculates idle cost for each request
    request_idle_cost = {}
    for request in range(1,len(requests)+1):
        request_idle_cost[request] = machines.get(requests.get(request).machine_id).idle_penalty
    
    #Calculates the idle days for each request
    idle_days_request = {}
    for request in range(1,len(requests)+1):
        idle_days_request[request] =  quicksum(day*routes_for_each_technician[technician][day][route][request] for day in range(1,dataset.days+1) for technician in range(1,len(technicians)+1) for route in range(0,len(technician_routes)))- (quicksum(day*routes_for_each_truck[day][truck][route][request] for day in range(1,dataset.days+1) for truck in range(0,number_of_trucks) for route in range(0, len(truck_routes)))+1)
    
    
    #Assigns a schedule to each technician
    technician_schedule = {}
    for technician in range(1,len(technicians)+1):       
        technician_schedule[technician] = {}
        for schedule in range(0,len(schedules)):
            technician_schedule[technician][schedule] = tools_model.addVar(vtype= GRB.BINARY)
     
    
    #Technician cost for each route
    technician_cost_each_route = {}
    for route in range(0,len(technician_routes)):
        technician_cost_each_route[route] = dataset.technician_day_cost + (dataset.technician_distance_cost*technician_routes[route][1])
             
    
    #Truck cost each route
    truck_cost_each_route = {}
    for route in range(0,len(truck_routes)):
        truck_cost_each_route[route] = dataset.truck_day_cost + (truck_routes[route][1]*dataset.truck_distance_cost)
    
    #The size of each request
    size_each_request = {}
    for request in range(1,len(requests)+1):
        size_each_request[request] = machines[requests[request].machine_id].size
    
    #Checks if a schedule has a certain day
    schedule_has_certain_day = {}
    for schedule in range(0,len(schedules)):
        schedule_has_certain_day[schedule] = {}
        for day in range(1,dataset.days+1):
            schedule_has_certain_day[schedule][day] = 0
            for i in range(0,len(schedules[schedule])):
                if day == schedules[schedule][i]:
                    schedule_has_certain_day[schedule][day] = 1
     
    distance_each_technician_route = {}
    for route in range(0,len(technician_routes)):
        distance_each_technician_route[route] = technician_routes[route][1]
    
    
    distance_each_truck_route = {}
    for route in range(0,len(truck_routes)):
        distance_each_truck_route[route] = truck_routes[route][1]
    
    quantity_each_request = {}
    for request in range(1,len(requests)+1):
        quantity_each_request[request] = requests[request].quantity
    
    
    for truck in range(0,number_of_trucks):
        for day in range(1,dataset.days +1):
            tools_model.addConstr(quicksum(distance_each_truck_route[route]*route__each_truck_each_day[day][truck][route] for route in range(0, len(truck_routes)) )<= dataset.truck_max_distance)
    
    
    #No more is delivered than the truck capacity
    for day in range(1,dataset.days+1):
        for truck in range(0,number_of_trucks):
            for route in range(0, len(truck_routes)):
                tools_model.addConstr(quicksum(quantity_each_request[request]*size_each_request[request]*routes_for_each_truck[day][truck][route][request] for request in range(1, len(requests)+1) )<= dataset.truck_capacity)
    
    
    #Every request is being delivered and request is in route
    for request in range(1,len(requests)+1):
        #trucks
        tools_model.addConstr(quicksum(routes_for_each_truck[day][truck][route][request]*route__each_truck_each_day[day][truck][route] for truck in range(0,number_of_trucks) for route in range(0, len(truck_routes)) for day in range(1,dataset.days+1)) == 1)
        tools_model.addConstr(quicksum(routes_for_each_truck[day][truck][route][request] for truck in range(0,number_of_trucks) for route in range(0, len(truck_routes)) for day in range(1,dataset.days+1)) == 1)
        
        #technicians
        tools_model.addConstr(quicksum(routes_for_each_technician[technician][day][route][request]*route_each_technician_each_day[technician][day][route] for technician in range(1,len(technicians)+1) for route in range(0,len(technician_routes)) for day in range(1,dataset.days+1)) == 1)
        tools_model.addConstr(quicksum(routes_for_each_technician[technician][day][route][request] for technician in range(1,len(technicians)+1) for route in range(0,len(technician_routes)) for day in range(1,dataset.days+1)) == 1)

    #No more than max installation can be installed on a day.
    for day in range(1, dataset.days+1):
        for technician in range(1,len(technicians)+1):
            tools_model.addConstr(quicksum(routes_for_each_technician[technician][day][route][request] for route in range(0,len(technician_routes)) for request in range(1,len(requests)+1))<= technicians[technician].max_installations_per_day)
    

    #Technician has not a day off when installing
    for technician in range(1,len(technicians)+1):
        for day in range(1,dataset.days+1):
             tools_model.addConstr(quicksum(route_each_technician_each_day[technician][day][route] for route in range(0,len(technician_routes)))<= quicksum(schedule_has_certain_day[schedule][day]*technician_schedule[technician][schedule]for schedule in range(0,len(schedules))))
             
    #Every technician has one schedule
    for technician in range(1,len(technicians)+1):
        tools_model.addConstr(quicksum(technician_schedule[technician][schedule] for schedule in range(0,len(schedules)) ) <= 1)
    
    #Technicians comes after delivery
    for request in range(1,len(requests)+1):
        tools_model.addConstr(quicksum(day*routes_for_each_truck[day][truck][route][request] for day in range(1,dataset.days+1) for truck in range(0,number_of_trucks) for route in range(0, len(truck_routes)) )<= (quicksum(day*routes_for_each_technician[technician][day][route][request] for day in range(1,dataset.days+1) for technician in range(1,len(technicians)+1) for route in range(0,len(technician_routes)))-1))
    
    
    #Technician has not a day off when installing
    for technician in range(1,len(technicians)+1):
        for day in range(1,dataset.days+1):
            tools_model.addConstr(quicksum( distance_each_technician_route[route]*route_each_technician_each_day[technician][day][route]for route in range(0,len(technician_routes)))<= technicians[technician].max_distance_per_day)

    #Idle costs + truck costs 
    tools_model.setObjective((quicksum(truck_cost_each_route[route]*route__each_truck_each_day[day][truck][route] for day in range(1,dataset.days+1) for truck in range(0,number_of_trucks) for route in range(0, len(truck_routes))))+(number_of_trucks*dataset.truck_cost) + (quicksum(route_each_technician_each_day[technician][day][route]*technician_cost_each_route[route]for technician in range(1,len(technicians)+1) for day in range(1,dataset.days+1) for route in range(0,len(technician_routes)))) + (quicksum(quantity_each_request[request]*idle_days_request[request]*request_idle_cost[request] for request in range(1,len(requests)+1) )) + (dataset.technician_cost * quicksum(technician_schedule[technician][schedule] for technician in range (1,len(technicians)+1) for schedule in range(0,len(schedules)))),GRB.MINIMIZE)

    tools_model.setParam("timeLimit", time_limit)
    tools_model.optimize()
    
    #Assigns a schedule to each technician
    for technician in range(1,len(technicians)+1):       
        for schedule in range(0,len(schedules)):
            technician_schedule[technician][schedule] = technician_schedule[technician][schedule].X
    
    for day in range(1,dataset.days+1):
        for truck in range(0,number_of_trucks):
            for route in range(0, len(truck_routes)): 
                route__each_truck_each_day[day][truck][route] = route__each_truck_each_day[day][truck][route].X
                if route__each_truck_each_day[day][truck][route] == 1:
                    print(day,truck,route, "hey")
    print("\n")
    
    for day in range(1,dataset.days+1):
        for truck in range(0,number_of_trucks):
            for route in range(0, len(truck_routes)):
                for request in range(1, len(requests)+1):
                    if day >= requests[request].start_day:
                        if day <= requests[request].end_day:
                            request_is_in_route = False
                            for j in range(0,len(truck_routes[route][0])):
                                if requests[request].location_id == truck_routes[route][0][j].id:
                                    request_is_in_route = True
                            if (request_is_in_route == True):
                                routes_for_each_truck[day][truck][route][request] = routes_for_each_truck[day][truck][route][request].X
                    if routes_for_each_truck[day][truck][route][request] == 1:
                        print("Day:", day)
                        print("Request:", request)
                        print("Truck:", truck)
                        print("Route:", route)
                        print("\n")
                    
    
    for day in range(1,dataset.days+1):
        for technician in range(1,len(technicians)+1):
            for route in range(0,len(technician_routes)):
                route_each_technician_each_day[technician][day][route] = route_each_technician_each_day[technician][day][route].X
                if route_each_technician_each_day[technician][day][route] == 1:
                    print(day,technician,route, "hey")
    
    for day in range(1,dataset.days+1):
        for technician in range(1,len(technicians)+1):
            for route in range(0,len(technician_routes)):
                for request in range(1,len(requests)+1):
                    request_is_in_route = False
                    for i in range(0,len(technician_routes[route][0])):
                        if requests[request].location_id == technician_routes[route][0][i].id:
                            request_is_in_route = True
                    if (request_is_in_route == True):
                        technician_has_machine_capability = True
                        for machine in range(0,len(technicians[technician].machine_capabilities)):
                            if technicians[technician].machine_capabilities[machine] == 0:
                                if (int(requests[request].machine_id)) == (machine+1):
                                    technician_has_machine_capability = False
                        if (technician_has_machine_capability == True):
                            if technicians[technician].location_id == technician_routes[route][0][0].id:
                                routes_for_each_technician[technician][day][route][request] = routes_for_each_technician[technician][day][route][request].X
                    if routes_for_each_technician[technician][day][route][request] == 1:
                        print("Day:", day)
                        print("Request:", request)
                        print("Technician:", technician)
                        print("Route:", route)
                        print("\n")
  
    number_of_truck_days = 0
    for day in range(1,dataset.days+1):
        for truck in range(0,number_of_trucks):
            truck_is_used_on_day = False
            for route in range(0, len(truck_routes)):
                for request in range(1,len(requests)+1):
                    if routes_for_each_truck[day][truck][route][request] == 1.0:
                        truck_is_used_on_day = True
            if truck_is_used_on_day:
                number_of_truck_days = number_of_truck_days+1
   
    #Calculates total truck distance
    total_truck_distance = 0
    locations_used = []
    for day in range(1,dataset.days+1):
        for truck in range(0,number_of_trucks):
            for route in range(0,len(truck_routes)):
                locations_used = []
                for request in range(1,len(requests)+1):
                    if routes_for_each_truck[day][truck][route][request] == 1.0:
                        if len(locations_used) == 0:
                            locations_used.append(requests[request].location_id)
                        else:
                            location_id_exists = False
                            for i in range(0,len(locations_used)):
                                if locations_used[i] == requests[request].location_id:
                                    location_id_exists = True
                            if location_id_exists == False:
                                locations_used.append(requests[request].location_id)
                current_location = '1'
                end_location = '1'
                for j in range(0,len(locations_used)):
                    print(locations_used)
                    print(locations['1'])
                    print(locations[locations_used[j]])
                    total_truck_distance = total_truck_distance + distance(locations[current_location], locations[locations_used[j]])
                    current_location = locations_used[j]
                if len(locations_used) >=1:  
                    total_truck_distance = total_truck_distance + distance(locations[current_location], locations[end_location])
    
    print("technicians:")
    total_technician_distance = 0
    for technician in range(1,len(technicians)+1):
        for day in range(1,dataset.days+1):
            for route in range(0,len(technician_routes)):
                locations_used = []
                for request in range(1,len(requests)+1):
                    if routes_for_each_technician[technician][day][route][request] == 1:
                        if requests[request].location_id == technicians[technician].location_id:
                            print("")
                        elif len(locations_used) == 0:
                            locations_used.append(requests[request].location_id)
                        else:
                            location_id_exists = False
                            for i in range(0,len(locations_used)):
                                if locations_used[i] == requests[request].location_id:
                                    location_id_exists = True
                            if location_id_exists == False:
                                locations_used.append(requests[request].location_id)
                current_location = technicians[technician].location_id
                end_location = technicians[technician].location_id
                for j in range(0,len(locations_used)):
                    print(technician, day, route)
                    print(locations_used)
                    print(current_location)
                    print(locations[locations_used[j]].id)
                    total_technician_distance = total_technician_distance + distance(locations[current_location], locations[locations_used[j]])
                    current_location = locations_used[j]
                if len(locations_used) >=1:  
                    total_technician_distance = total_technician_distance + distance(locations[current_location], locations[end_location])
    
    number_of_technicians_used = 0
    for technician in range(1,len(technicians)+1):
        technician_used = False
        for day in range(1,dataset.days+1):
            for route in range(0,len(technician_routes)):
                if route_each_technician_each_day[technician][day][route] == 1.0:
                    technician_used = True
        if technician_used:
            number_of_technicians_used = number_of_technicians_used+1
    
    #Calculates number of technicians days
    number_of_technician_days = 0
    for day in range(1,dataset.days+1):
        for technician in range(1,len(technicians)+1):
            technician_is_used = False
            for route in range(0,len(technician_routes)):    
                for request in range(1, len(requests)+1):
                    if routes_for_each_technician[technician][day][route][request] == 1:
                        technician_is_used = True
            if technician_is_used:
                number_of_technician_days = number_of_technician_days + 1
    
    for request in range(1,len(requests)+1):
        idle_days_request[request] =  quicksum(day*routes_for_each_technician[technician][day][route][request] for day in range(1,dataset.days+1) for technician in range(1,len(technicians)+1) for route in range(0,len(technician_routes)) )- (quicksum(day*routes_for_each_truck[day][truck][route][request] for day in range(1,dataset.days+1) for truck in range(0,number_of_trucks) for route in range(0, len(truck_routes)))+1)  
    
    idle_costs = 0
    for request in range(1,len(requests)+1):
        idle_costs = idle_costs + (quantity_each_request[request]*idle_days_request[request]*request_idle_cost[request])
    
    
    truck_cost =quicksum(truck_cost_each_route[route]*route__each_truck_each_day[day][truck][route] for day in range(1,dataset.days+1) for truck in range(0,number_of_trucks) for route in range(0, len(truck_routes)))
    print("truck cost: ", truck_cost)
    other_truck_cost = number_of_trucks*dataset.truck_cost
    print("other truck cost: ", other_truck_cost)
    technician_costs = quicksum(route_each_technician_each_day[technician][day][route]*technician_cost_each_route[route]for technician in range(1,len(technicians)+1) for day in range(1,dataset.days+1) for route in range(0,len(technician_routes)))
    print("technician cost: ", technician_costs)
    other_technician_cost = dataset.technician_cost * quicksum(technician_schedule[technician][schedule] for technician in range (1,len(technicians)+1) for schedule in range(0,len(schedules)))
    print("other technician cost: ", other_technician_cost)
    idle_costs = quicksum(quantity_each_request[request]*idle_days_request[request]*request_idle_cost[request] for request in range(1,len(requests)+1) )
    print("idle costs: ", idle_costs)
    
    total_costs = total_truck_distance*dataset.truck_distance_cost + number_of_truck_days*dataset.truck_day_cost + int(idle_costs.getValue()) +number_of_trucks*dataset.truck_cost +number_of_technician_days*dataset.technician_day_cost +number_of_technicians_used*dataset.technician_cost + total_technician_distance*dataset.technician_distance_cost
    
    dataset_name = dataset.name
    
    file = open(sol_path, 'w')
    
    file.write("DATASET = VeRoLog solver challenge 2019\n")
    file.write(f"NAME = {dataset_name}\n\n")
    file.write(f"TRUCK_DISTANCE = {round(total_truck_distance)}\n")
    file.write(f"NUMBER_OF_TRUCK_DAYS = {number_of_truck_days}\n")
    file.write(f"NUMBER_OF_TRUCKS_USED = {number_of_trucks}\n")
    file.write(f"TECHNICIAN_DISTANCE = {round(total_technician_distance)}\n")
    file.write(f"NUMBER_OF_TECHNICIAN_DAYS = {number_of_technician_days}\n")
    file.write(f"NUMBER_OF_TECHNICIANS_USED = {number_of_technicians_used}\n")
    file.write(f"IDLE_MACHINE_COSTS = {int(idle_costs.getValue())}\n")
    file.write(f"TOTAL_COST = {round(total_costs)}\n\n")
    
    for day in range(1,dataset.days+1):
        number_of_trucks_day = 0
        for truck in range(0,number_of_trucks):
            truck_used = False
            for route in range(0,len(truck_routes)):
                for request in range(1, len(requests)+1):
                    if routes_for_each_truck[day][truck][route][request] == 1:
                        truck_used = True
            if truck_used:
                number_of_trucks_day = number_of_trucks_day  + 1
        
        number_of_technicians = 0
        for technician in range(1,len(technicians)+1):
            technician_used = False
            for route in range(0,len(technician_routes)):
                for request in range(1, len(requests)+1):
                    if routes_for_each_technician[technician][day][route][request] == 1.0:
                        technician_used = True
            if technician_used:
                number_of_technicians = number_of_technicians +1
        
        file.write(f"DAY = {day}\n")
        file.write(f"NUMBER_OF_TRUCKS = {number_of_trucks_day}")
        
        
        for truck in range(0,number_of_trucks):
            is_already_used = False
            truck_is_used = False
            for route in range(0,len(truck_routes)):
                for request in range(1, len(requests)+1):
                    if routes_for_each_truck[day][truck][route][request] == 1:
                        truck_is_used = True
                if truck_is_used:
                    if route__each_truck_each_day[day][truck][route] == 1.0:
                        if is_already_used == True:
                            file.write(f"0 ")
                        if is_already_used == False:
                                file.write(f"\n{truck} ")
                                is_already_used = True
                        for i in range(0,len(truck_routes[route][0])-1):
                            for request in range(1, len(requests)+1):
                                if routes_for_each_truck[day][truck][route][request] == 1:
                                    if requests[request].location_id == truck_routes[route][0][i].id:
                                        file.write(f"{request} ")
    
        file.write(f"\nNUMBER_OF_TECHNICIANS = {number_of_technicians}")
        
        for technician in range(1,len(technicians)+1):
            technician_is_used = False
            for route in range(0,len(technician_routes)):
                for request in range(1, len(requests)+1):
                    if routes_for_each_technician[technician][day][route][request] == 1:
                        technician_is_used = True
                if technician_is_used:
                    if route_each_technician_each_day[technician][day][route] == 1.0:
                        file.write(f"\n{technician} ")
                        for i in range(0,len(technician_routes[route][0])-1):
                            for request in range(1, len(requests)+1):
                                if routes_for_each_technician[technician][day][route][request] == 1:
                                    if requests[request].location_id == technician_routes[route][0][i].id:
                                        file.write(f"{request} ")
        file.write("\n\n")
    
    return

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

    Optimize(dataset, machines, locations, requests, technicians, solution_file_path, timelim)
    print("Code has no errors")
  