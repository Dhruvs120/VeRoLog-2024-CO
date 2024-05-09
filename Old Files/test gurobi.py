#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 13:40:34 2024

@author: stijnsmoes
"""



from COread2024 import *
import gurobipy as gp
import itertools
from gurobipy import  GRB, quicksum
import math

vending_machine_model = gp.Model("Machines")


def start_location(coordinates_list, start_location_id):
    for location in coordinates_list.values():
        if coordinates_list[1] == start_location_id:
            return location

def distance(coordinates1, coordinates2):
    if coordinates1 is None or coordinates2 is None:
        return 0
    
    distance = math.ceil(np.sqrt(pow(coordinates2[0] -  coordinates1[0],2) + pow(coordinates2[1] -  coordinates1[1],2)))
    return distance

def find_routes(start_location_id, truck_max_distance,coordinates_list):
    # Filter coordinates_list to include only those with ID not equal to start_location_id
    destinations = []
    for loc in coordinates_list.values():
        if loc[0] != start_location_id:
            destinations.append(loc)
    routes = []
    

    # Generate all possible permutations of destinations
    for r in range(1, len(destinations) + 1):
        for perm in itertools.permutations(destinations, r):
            route = [start_location(coordinates_list, start_location_id)] + list(perm) + [start_location(coordinates_list, start_location_id)]
            total_distance = sum(distance(route[i], route[i+1]) for i in range(0,len(route)-1))
            if total_distance <= truck_max_distance:
                routes.append([route,total_distance])
    return routes



def possible_schedules():
    
    days = []
    for i in range(1,len(days)+1):
        days.append(i)
    
    schedules = []
    for r in range(1, len(days)+1):
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

def Optimize(machines, coordinates_list, requests,technicians ):
    
    
        
    truck_routes = find_routes('1', truck_max_distance,coordinates_list)
    
    technician_routes = []
    for technician in technicians.values():
        routes = find_routes(technician['location_id'], technician['tech_max_distance'], coordinates_list)
        technician_routes.extend(routes)
    
    schedules = possible_schedules()
    
    #Xr_d
    route_each_day = {}
    for day in range(1,days+1):
        route_each_day[day] = {}
        for i in range(0,len(truck_routes)):
            route_each_day[day][i] = vending_machine_model.addVar(vtype = GRB.BINARY)
    
    #N_trucks
    number_of_trucks = vending_machine_model.addVar(vtype=GRB.INTEGER)
    
    #y_p_t,d
    technician_tour_day = {}
    for technician in range(0,len(technicians)):
        technician_tour_day[technician] = {}
        for day in range(1,days +1):
            technician_tour_day[technician][day] = {}
            for route in range(0,len(technician_routes)):
                if technician_routes[route][0][0] == technicians[technician+1]['location_id']:
                    technician_tour_day[technician][day][route] = vending_machine_model.addVar(vtype=GRB.BINARY)
                else:
                    technician_tour_day[technician][day][route] = 0
                    
    #request_on_route_and_day = {}
    #for request in range(1,len(requests)+1):
        #request_on_route_and_day[request] = {}
        #for route in range(0,len(truck_routes)):
            #request_on_route_and_day[request][route] = {}
            #for day in range(1,dataset.days+1):
                #request_on_route_and_day[request][route][day] = vending_machine_model.addVar(vtype=GRB.BINARY)
    
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
            technician_schedule[technician][schedule] = vending_machine_model.addVar(vtype= GRB.BINARY)
    
    #b_t,m
    request_is_in_tecnician_route = {}
    for route in range(0,len(technician_routes)):
        request_is_in_tecnician_route[route] = {}
        for request in range(1,len(requests)+1):
            request_is_in_tecnician_route[route][request] = 0
            for i in range(0,len(technician_routes[route][0])):
                if requests[request]['location_id'] == technician_routes[route][0][i]:
                    request_is_in_tecnician_route[route][request] = 1

    #A_rm
    request_is_in_truck_route = {}
    for route in range(0,len(truck_routes)):
        request_is_in_truck_route[route] = {}
        for i in range(1,len(requests)+1):
            request_is_in_truck_route[route][i] = 0
            for j in range(0,len(truck_routes[route][0])):
                if requests[i]['location_id'] == truck_routes[route][0][j]:
                    request_is_in_truck_route[route][i] = 1
            
    #C_r
    truck_cost_each_route = {}
    for i in range(0,len(truck_routes)):
        truck_cost_each_route[i] = truck_day_cost + (truck_routes[i][1]*truck_distance_cost)
        
    #e_s,d
    schedule_has_certain_day = {}
    for schedule in range(0,len(schedules)):
        schedule_has_certain_day[schedule] = {}
        for day in range(0,days+1):
            schedule_has_certain_day[schedule][day] = 0
            for i in range(0,len(schedules[schedule])):
                if day == schedules[schedule][i]:
                    schedule_has_certain_day[schedule][day] = 1
     
    #h_t_p
    technician_cost_per_tour = {}
    for technician in range(0,len(technicians)):
        technician_cost_per_tour[technician] = {}
        for route in range(0,len(technician_routes)):
            technician_cost_per_tour[technician][route] = 0
            if technician_routes[route][0][0] == technicians[technician+1]['location_id']:
                technician_cost_per_tour[technician][route] = technician_day_cost + technician_distance_cost*technician_routes[route][1]
                
    
    #W_m
    idle_days_request = {}
    for request in range(1,len(requests)+1):
        last_day = quicksum(day*request_is_in_tecnician_route[route][request]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,days +1))
        first_day = quicksum(day*request_is_in_truck_route[route][request]*route_each_day[day][route] for day in range(1,days+1) for route in range(0,len(truck_routes)))
        idle_days_request[request] = last_day - first_day
            
    #C_m
    request_idle_cost = {}
    for request in range(1,len(requests)+1):
        request_idle_cost[request] = machines_set.get(requests[request]['machine_id'])['idle_fee']
    
    #trying
    #for route in range(0,len(truck_routes)):
        #for day in range(1,dataset.days+1):
            #vending_machine_model.addConstr(quicksum(capacity_each_request[request]*quantity_each_request[request]*request_on_route_and_day[request][route][day] for request in range(1,len(requests)+1) ) <= dataset.truck_capacity)
    
    #trying
    #for request in range(1,len(requests)+1):
        #vending_machine_model.addConstr(quicksum(request_on_route_and_day[request][route][day] for day in range(1,dataset.days+1) for route in range(0,len(truck_routes))) == 1)
    
    for day in range(1,days+1):
        vending_machine_model.addConstr(quicksum(route_each_day[day][i] for i in range(0,len(truck_routes))) <= number_of_trucks)
    
    for request in range(1,len(requests)+1):
        vending_machine_model.addConstr(quicksum(request_is_in_truck_route[route][request]*route_each_day[day][route] for route in range(0,len(truck_routes)) for day in range(1,days+1)) == 1)
    
        
    for technician in range(0,len(technicians)):
        vending_machine_model.addConstr(quicksum(technician_schedule[technician][schedule] for schedule in range(0,len(schedules)) ) <= 1)
    
    for technician in range(0,len(technicians)):
        for day in range(1,days+1):
            vending_machine_model.addConstr(quicksum(technician_tour_day[technician][day][route] for route in range(0,len(technician_routes)))<= quicksum(schedule_has_certain_day[schedule][day]*technician_schedule[technician][schedule]for schedule in range(0,len(schedules))))
            #vending_machine_model.addConstr( quicksum(schedule_has_certain_day[schedule][day]*technician_schedule[technician][schedule]for schedule in range(0,len(schedules))) == 1)
    
    for request in range(1,len(requests)+1):
        vending_machine_model.addConstr( quicksum(request_is_in_tecnician_route[route][request]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,days +1) )== 1)
    
    for day in range(1,days+1):
        for request in range(1,len(requests)+1):
            vending_machine_model.addConstr(quicksum(request_is_in_tecnician_route[route][request]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) ) <= quicksum(request_is_in_truck_route[route][request]*route_each_day[day][route] for day in range(1,days) for route in range(0,len(truck_routes))))
    
    #trying
    #for day in range(1,dataset.days+1):
        #for route in range(0,len(truck_routes)):
            #vending_machine_model.addConstr( route_each_day[day][route] == quicksum(request_on_route_and_day[request][route][day] for request in range(1,len(requests)+1)))
    
    
    for request in range(1,len(requests)+1):
        vending_machine_model.addConstr(idle_days_request[request] >= 0)
    #vending_machine_model.setObjective(quicksum(truck_cost_each_route[i] * quicksum(route_each_day[day][i] for day in range(1,dataset.days+1) ) for i in range(0,len(truck_routes))),GRB.MINIMIZE)
    #vending_machine_model.setObjective(number_of_trucks*dataset.truck_cost,GRB.MINIMIZE)
    #vending_machine_model.setObjective(quicksum(request_idle_cost[request]*idle_days_request[request] for request in range(1,len(requests)+1)),GRB.MINIMIZE)
    #vending_machine_model.setObjective(quicksum(technician_cost_per_tour[technician][route]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,dataset.days +1)),GRB.MINIMIZE)
    vending_machine_model.setObjective((technician_cost * quicksum(technician_schedule[technician][schedule] for technician in range (0,len(technicians)) for schedule in range(0,len(schedules))))+(number_of_trucks*truck_cost)+(quicksum(truck_cost_each_route[i] * quicksum(route_each_day[day][i] for day in range(1,days+1) ) for i in range(0,len(truck_routes))))+(quicksum(request_idle_cost[request]*idle_days_request[request] for request in range(1,len(requests)+1))) + (quicksum(technician_cost_per_tour[technician][route]*technician_tour_day[technician][day][route] for technician in range(0,len(technicians)) for route in range(0,len(technician_routes)) for day in range(1,days +1))), GRB.MINIMIZE)
    vending_machine_model.optimize()
    
    #for request in range(1,len(requests)+1):
        #for day in range(1,dataset.days+1):
            #for route in range(0,len(truck_routes)):
                #if request_on_route_and_day[request][route][day].x ==1:
                    #print("request:", request, "day:",day)
    
    print(number_of_trucks)
    
    total_truck_distance = 0
    for day in range(1,days+1):
        for i in range(0,len(truck_routes)):
            if route_each_day[day][i].X == 1.0:
                total_truck_distance = total_truck_distance + truck_routes[i][1]
    
    
  
Optimize(machines, coordinates_list, requests, technicians)
