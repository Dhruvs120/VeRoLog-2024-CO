import gurobipy as gp
import itertools
from gurobipy import GRB, quicksum
from classes import Dataset, Machine, Location, Request, Technician
import numpy as np
from partFunctions import start_location, distance
from routeFinder import find_routes
from scheduleGenerator import possible_schedules
from fileReader import ReadInstance

tools_model = gp.Model("Tools")

def Optimize(dataset, machines, locations, requests,technicians):
        
    truck_routes = find_routes('1', dataset.truck_max_distance,locations)
    
    technician_routes = []
    for technician in technicians.values():
        routes = find_routes(technician.location_id, 10000000, locations)
        technician_routes.extend(routes)
    
    schedules = possible_schedules(dataset, requests, machines)
    
    #Xr_d
    route_each_day = {}
    for day in range(1,dataset.days+1):
        route_each_day[day] = {}
        for route in range(0,len(truck_routes)):
            route_each_day[day][route] = tools_model.addVar(vtype = GRB.BINARY)
    
    #N_trucks
    number_of_trucks = tools_model.addVar(vtype=GRB.INTEGER)
    
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
    technician_cost_each_route = {}
    for technician in range(0,len(technicians)):
        technician_cost_each_route[technician] = {}
        for route in range(0,len(technician_routes)):
            technician_cost_each_route[technician][route] = 1000000
            if technician_routes[route][0][0].id == technicians[technician+1].location_id:
                technician_cost_each_route[technician][route] = dataset.technician_day_cost + dataset.technician_distance_cost*technician_routes[route][1]
                
    
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
    
    
    
    
    #New code:
        
    
    #Number of routes taken on a day is less or equals to number of trucks
    for day in range(1,dataset.days+1):
        tools_model.addConstr(quicksum(route_each_day[day][route] for route in range(0,len(truck_routes))) <= number_of_trucks)
    
    #Every request is being delivered 
    for request in range(1,len(requests)+1):
        tools_model.addConstr(quicksum(request_is_in_truck_route[route][request]*route_each_day[day][route] for route in range(0,len(truck_routes)) for day in range(1,dataset.days+1)) == 1)
    
    #Every request is installed
    #Machine is being delivered first before installed
    #Ever truck used does not exceeds its maximum capacity
    #Every techinician does not exceeds its maximum installations
    
    #Each technician has a schedule he follows
        
    
    
    
    
    #Trying to solve truck capacity constraints


    # Define truck capacity
    # truck_capacity = 15  # Assuming a capacity of 15 units for each truck

    # # Define the size of each request (assuming it's stored in the requests dictionary)
    # request_sizes = {request_id: requests[request_id].quantity * machines[requests[request_id].machine_id].size for request_id in range(1, len(requests) + 1)}
    
    # for route in range(len(truck_routes)):
    #     tools_model.addConstr(quicksum(request_sizes[request_id] * request_is_in_truck_route[route][request_id] for request_id in range(1, len(requests) + 1)) <= truck_capacity)
      
    #Original code
    """
    for route in range(len(truck_routes)):
        tools_model.addConstr(quicksum(requests[request].quantity * request_is_in_truck_route[route][request]for request in range(1, len(requests) + 1)) <= 15)
    
    for request in range(1, len(requests) + 1):
        tools_model.addConstr(quicksum(requests[request].quantity * request_is_in_truck_route[route][request]for route in range(len(truck_routes))) == 1)
    """
    
    
    
    
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
    
    for request in range(1,len(requests)+1):
        tools_model.addConstr(idle_days_request[request] >= 0)
    
    
    
    #tools_model.setObjective(quicksum(truck_cost_each_route[i] * quicksum(route_each_day[day][i] for day in range(1,dataset.days+1) ) for i in range(0,len(truck_routes))),GRB.MINIMIZE)
    #tools_model.setObjective(number_of_trucks*dataset.truck_cost,GRB.MINIMIZE)
    #tools_model.setObjective(quicksum(request_idle_cost[request]*idle_days_request[request] for request in range(1,len(requests)+1)),GRB.MINIMIZE)
    #tools_model.setObjective(quicksum(technician_cost_per_tour[technician][route]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,dataset.days +1)),GRB.MINIMIZE)
    tools_model.setObjective((dataset.technician_cost * quicksum(technician_schedule[technician][schedule] for technician in range (0,len(technicians)) for schedule in range(0,len(schedules))))+(number_of_trucks*dataset.truck_cost)+(quicksum(truck_cost_each_route[i] * quicksum(route_each_day[day][i] for day in range(1,dataset.days+1) ) for i in range(0,len(truck_routes))))+(quicksum(request_idle_cost[request]*idle_days_request[request] for request in range(1,len(requests)+1))) + (quicksum(technician_cost_each_route[technician][route]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,dataset.days +1))), GRB.MINIMIZE)
    tools_model.optimize()
    
    
    
    
    
    #Xr_d
    for day in range(1,dataset.days+1):
        for route in range(0,len(truck_routes)):
            route_each_day[day][route] = route_each_day[day][route].X
            
            
    #N_trucks
    number_of_trucks = number_of_trucks.X
    
    
    #y_p_t,d
    for technician in range(0,len(technicians)):
        for day in range(1,dataset.days +1):
            for route in range(0,len(technician_routes)):
                if technician_routes[route][0][0].id == technicians[technician+1].location_id:
                    technician_tour_day[technician][day][route] = technician_tour_day[technician][day][route].X
                    
                else:
                    technician_tour_day[technician][day][route] = 0
                
    
    
    #z_ps
    for technician in range(0,len(technicians)):
        for schedule in range(0,len(schedules)):
            technician_schedule[technician][schedule] = technician_schedule[technician][schedule].X
    
    
    #W_m
    idle_days_request = {}
    for request in range(1,len(requests)+1):
        last_day = quicksum(day*request_is_in_tecnician_route[route][request]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,dataset.days +1))
        first_day = quicksum(day*request_is_in_truck_route[route][request]*route_each_day[day][route] for day in range(1,dataset.days+1) for route in range(0,len(truck_routes)))
        idle_days_request[request] = last_day - first_day  
    
    #Calculates idle machine costs
    idle_machine_costs = 0
    for request in range(1,len(requests)+1):
        idle_machine_costs = idle_machine_costs + (idle_days_request[request]*request_idle_cost[request])
    
    
    #Calculates total truck distance
    total_truck_distance = 0
    for day in range(1,dataset.days+1):
        for i in range(0,len(truck_routes)):
            if route_each_day[day][i] == 1.0:
                total_truck_distance = total_truck_distance + truck_routes[i][1]
    
    #Calculates number of truck days
    number_of_truck_days = 0
    for day in range(1,dataset.days+1):
        truck_used = False
        for i in range(0,len(truck_routes)):
            if route_each_day[day][i] == 1.0:
                truck_used = True
        if truck_used:
            number_of_truck_days = number_of_truck_days + 1
    
    #Calculates total technician distance
    total_technician_distance = 0
    for technician in range(0,len(technicians)):
        for day in range(1,dataset.days+1):
            for route in range(0,len(technician_routes)):
                if technician_tour_day[technician][day][route] == 1.0:
                    total_technician_distance = total_technician_distance + technician_routes[i][1]
    
    
    #Calculates number of technicians used
    number_of_technicians_used = 0
    for technician in range(0,len(technicians)):
        technician_used = False
        for day in range(1,dataset.days +1):
            for route in range(0,len(technician_routes)):
                if technician_tour_day[technician][day][route] == 1.0:
                    technician_used = True
        if (technician_used):
            number_of_technicians_used = number_of_technicians_used + 1
    
    #Calculates number of technicians days
    number_of_technician_days = 0
    for day in range(1,dataset.days+1):
        technician_used = False
        for route in range(0,len(technician_routes)):
            for technician in range(0,len(technicians)):
                if technician_tour_day[technician][day][route] == 1.0:
                    technician_used = True
        if technician_used:
            number_of_technician_days = number_of_technician_days + 1
    
    print("\n\nTotal truck distance:", total_truck_distance)
    print("Number of trucks days", number_of_truck_days )
    print("Number of trucks used:", number_of_trucks)
    print("Total technician distance:", total_technician_distance)
    print("Number of technician days:", number_of_technician_days )
    print("Number of technician used:", number_of_technicians_used)
    print("Idle machine costs:", idle_machine_costs )
    print("Total costs:", tools_model.objVal)
    
    file_path = "/Users/Dhruv/Downloads/Vakken/Combinatorial Optimization/solution/CO_Case2401ol.txt" # Specify the path and filename
    file = open(file_path, 'w')
    
    file.writelines([
        f"DATASET = VeRoLog solver challenge 2019\n",
        f"NAME = {dataset.name}\n",
        f"TRUCK_DISTANCE = {total_truck_distance}\n",
        f"NUMBER_OF_TRUCK_DAYS = {number_of_truck_days}\n",
        f"NUMBER_OF_TRUCKS_USED = {number_of_trucks}\n",
        f"TECHNICIAN_DISTANCE = {total_technician_distance}\n",
        f"NUMBER_OF_TECHNICIAN_DAYS = {number_of_technician_days}\n",
        f"NUMBER_OF_TECHNICIANS_USED = {number_of_technicians_used}\n",
        f"IDLE_MACHINE_COSTS = {idle_machine_costs}\n",
        f"TOTAL_COST = {tools_model.objVal}\n"
    ])
     
    return None # Might be replaceable with a break eventually, leaving it here for now


if __name__ == "__main__":
    instance_file = "/Users/Dhruv/Downloads/Vakken/Combinatorial Optimization/VeRoLog-2024-CO/instances 2024/CO_Case2401.txt" # Replace with your actual file path
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
    print("Code has no errors")
  
    # Return a specific technician's attribute based on their id    
    # print(technicians.get(1).machine_capabilities)
