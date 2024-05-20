#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 16:22:01 2024

@author: stelianmunteanu
"""

import COread2024 as read
import Tools as tl
from collections import defaultdict
from itertools import combinations

def init_route_schedules():
    schedule = {}
    for day in range(1, read.days + 1):
        schedule[day] = []
    return schedule
    

# Assign requests to be delivered in the first day
def assign():
    schedule = init_route_schedules()
    for day in range(1, read.days+1):
        for i in range(1, read.requests_size + 1):
            if read.requests[i]["last_day"] - 1 == day:    
                schedule[day].append(i)
    return schedule

#Get the distance that must be done by a truck in order to deliver a list of request
#assuming the truck starts at the depot and visits all the requests in the order they are in the list
def get_distance(req_list):
    depot_location = read.coordinates_list[1]
    first_customer_location = read.coordinates_list[read.requests[req_list[0]]["location_id"]]
    distance = tl.calculates_distance(depot_location, first_customer_location)
    for i in range (1, len(req_list)):
        previous_customer_location = read.coordinates_list[read.requests[req_list[i - 1]]["location_id"]]
        actual_customer_location = read.coordinates_list[read.requests[req_list[i]]["location_id"]]
        distance = distance + tl.calculates_distance(previous_customer_location, actual_customer_location)
    final_cust = read.coordinates_list[read.requests[req_list[-1]]["location_id"]]
    distance = distance + tl.calculates_distance(final_cust, depot_location)
    return distance

#Check if a list of requests concerns machines with in the maximum capacity of a truck
def is_in_maxim_cap(req_list):
    capacity = 0
    for i in req_list:
        number_machines = read.requests[i]["nr_machines"]
        machine_type = read.requests[i]["machine_id"]
        machine_size = read.machines_size[machine_type]
        req_capacity = number_machines * machine_size
        capacity = capacity + req_capacity
    if capacity <= read.truck_capacity:
        return True
    else: return False

#returns all possible combinations out of the numbers of a list: numbers
def generate_all_combinations(numbers):
    all_combinations = []
    for r in range(len(numbers), 0, -1):
        all_combinations.extend(combinations(numbers, r))
    return all_combinations

#checks if 2 lists have at leat one common element
def has_common_element(list1, list2):
    for element in list1:
        if element in list2:
            return True
    return False

#routing algorithm starting from the brut route
def creates_route_schedule(brut_route_schedule):
    route_schedule = defaultdict(list)
    for day in range (1, read.days + 1):
        route_schedule[day]
        check_req = [] 
        routes_list = generate_all_combinations(brut_route_schedule[day])
        for route in routes_list:
            if not has_common_element(check_req, route) and is_in_maxim_cap(route) and get_distance(route) <= read.truck_max_distance:
                check_req.extend(route)
                route_schedule[day].append(route)

    return route_schedule

#makes sure the values of the dictionary d_schedule are all lists of lists 
def formats_route_schedule(schedule):      
    for key, value in schedule.items():
        if not value:
            schedule[key] = [()]
    return schedule
            
            
def calculates_routing_costs(route, get_all_info):
    total_distance = sum(get_distance(j) for sublist in route.values() for j in sublist if j)         
    maxim_trucks = max(len(sublist) for sublist in route.values())   
    total_trucks = sum(1 for sublist in route.values() for item in sublist if item)             
    total_routing_costs = read.truck_distance_cost * total_distance + maxim_trucks * read.truck_cost + total_trucks * read.truck_day_cost
    if get_all_info:
        return total_distance, total_trucks, maxim_trucks, total_routing_costs 
    else: return total_routing_costs
    

         
        






        
        


            