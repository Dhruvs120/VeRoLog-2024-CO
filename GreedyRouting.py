#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 16:22:01 2024

@author: stelianmunteanu
"""

from COread2024 import *
from collections import defaultdict


global d_schedule
global route_schedule
global truck_days

d_schedule = {}
route_schedule = {}
truck_days = 0

for day in range(1, days + 1):
    d_schedule[day] = []
    route_schedule[day] = []


def calculates_distance(coordinates1, coordinates2):
    distance = round(np.sqrt(pow(coordinates2[0] -  coordinates1[0],2) + pow(coordinates2[1] -  coordinates1[1],2)),2)
    return distance
    

# Assign requests to delivery schedule based on first day 
for day in range(1, days+1):
    for i in range(1, requests_size + 1):
        if requests[i]["first_day"] == day:    
            d_schedule[day].append(i)


#Get the distance that must be done by a truck in order to deliver a list of request
#assuming the truck starts at the depot and visits all the requests in the order they are in the list
def get_distance(req_list):
    depot_location = coordinates_list[1]
    first_customer_location = coordinates_list[requests[req_list[0]]["location_id"]]
    distance = calculates_distance(depot_location, first_customer_location)
    for i in range (1, len(req_list)):
        previous_customer_location = coordinates_list[requests[req_list[i - 1]]["location_id"]]
        actual_customer_location = coordinates_list[requests[req_list[i]]["location_id"]]
        distance = distance + calculates_distance(previous_customer_location, actual_customer_location)
    final_cust = coordinates_list[requests[req_list[-1]]["location_id"]]
    distance = distance + calculates_distance(final_cust, depot_location)
    return distance

#Check if a list of requests concerns machines with in the maximum capacity of a truck
def is_in_maxim_cap(req_list):
    capacity = 0
    for i in req_list:
        number_machines = requests[i]["nr_machines"]
        machine_type = requests[i]["machine_id"]
        machine_size = machines_size[machine_type]
        req_capacity = number_machines * machine_size
        capacity = capacity + req_capacity
    if capacity <= truck_capacity:
        return True
    else: return False
    

#From a list of requests returns the id of the request with the latest due date
#This function is not used yet, it may be useful for further optimization
def latest_due_date(req_list):
    req_result = None
    req_max_date = 0
    for i in req_list:
        if requests[i]["last_day"] > req_max_date:
            req_max_date = requests[i]["last_day"]
            req_result = i
    return req_result

#From a list of requests returns the id of the request which needs the largest capacity
def get_high_cap(req_list):
    result_id = None
    highest_cap = 0
    for i in req_list:
       number_machines = requests[i]["nr_machines"]
       machine_type = requests[i]["machine_id"]
       machine_size = machines_size[machine_type]
       req_capacity = number_machines * machine_size
       capacity = capacity + req_capacity
       if capacity > highest_cap:
           highest_cap = capacity
           result_id = i           
    return result_id


# From a list of request returns a list of requests that can be delivered the next day based on their due date
#and a second list of requests that can not be delivered  on a later day(thus, must be delivered on the 'actual_day')
def moved_requests(req_list, actual_day):
    to_move_req = []
    to_keep_req = []
    for i in req_list:
        if actual_day < requests[i]["last_day"] - 1:
            to_move_req.append(i)
        else: to_keep_req.append(i)
    return to_move_req, to_keep_req

        
#groups all the requests with respect to the due day (routes the requests as late as possible)
def assign_as_late():
    for i in range(1, days + 1):
        schedule_day = d_schedule[i]
        to_move_req, to_keep_req = moved_requests(schedule_day, i)
        if i != days and to_move_req:
            d_schedule[i + 1].extend(to_move_req)
        d_schedule[i] = to_keep_req
  

#greedy routing algorithm
def creates_route_schedule():
    check_req = [] 
    for i in range (1, days + 1):
        routes_list = []
        for j in range(len(d_schedule[i])):
            help_list = []
            if d_schedule[i][j] not in check_req:
                help_list.append(d_schedule[i][j])
                check_req.append(d_schedule[i][j])
                if j != len(d_schedule[i]) - 1:
                    for k in range(j + 1, len(d_schedule[i])):                  
                        if d_schedule[i][k] not in check_req:
                            help_list.append(d_schedule[i][k])
                            if get_distance(help_list) <= truck_max_distance and is_in_maxim_cap(help_list):
                                check_req.append(d_schedule[i][k])
                            else: help_list.remove(d_schedule[i][k])
                            
                        if k == len(d_schedule[i]) - 1 and help_list:
                            routes_list.append(help_list)                           
                else: 
                    routes_list.append(help_list)
        route_schedule[i] = routes_list
    

#makes sure the values of the dictionary d_schedule are all lists of lists 
def formats_route_schedule():         
    for key, value in route_schedule.items():
        if isinstance(value, list) and not any(isinstance(sublist, list) for sublist in value):
            route_schedule[key] = [[]]
        
        
assign_as_late()  
creates_route_schedule()
formats_route_schedule()

total_distance = 0
maxim_trucks = 0
total_trucks = 0
total_routing_costs = 0

def calculates_routing_costs():
    global total_distance
    global maxim_trucks
    global total_trucks
    global total_routing_costs

    total_distance = sum(get_distance(j) for sublist in route_schedule.values() for j in sublist if j)          
    maxim_trucks = max(len(sublist) for sublist in route_schedule.values())   
    total_trucks =  max(len(sublist) for sublist in route_schedule.values())             
    total_routing_costs = truck_distance_cost * total_distance + maxim_trucks * truck_cost + total_trucks * truck_day_cost
    return total_routing_costs

calculates_routing_costs()

# Calculate truck days 
for day in range(1, days+1):
    if len(d_schedule[day]) != 0:
        truck_days += 1
        
        


            
