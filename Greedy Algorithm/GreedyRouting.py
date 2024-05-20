#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 16:22:01 2024

@author: stelianmunteanu
"""

import ReadInput as read
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
            if read.requests[i]["first_day"] == day:    
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
    
    
#From a list of requests returns the id of the request with the latest due date
#This function is not used yet, it may be useful for further optimization
def latest_due_date(req_list):
    req_result = None
    req_max_date = 0
    for i in req_list:
        if read.requests[i]["last_day"] > req_max_date:
            req_max_date = read.requests[i]["last_day"]
            req_result = i
    return req_result

#From a list of requests returns the id of the request which needs the largest capacity
def get_high_cap(req_list):
    result_id = None
    highest_cap = 0
    for i in req_list:
       number_machines = read.requests[i]["nr_machines"]
       machine_type = read.requests[i]["machine_id"]
       machine_size = read.machines_size[machine_type]
       req_capacity = number_machines * machine_size
       if req_capacity > highest_cap:
           highest_cap = req_capacity
           result_id = i           
    return result_id


# From a list of request returns a list of requests that can be delivered the next day based on their due date
#and a second list of requests that can not be delivered  on a later day(thus, must be delivered on the 'actual_day')
def moved_requests(req_list, actual_day):
    to_move_req = []
    to_keep_req = []
    for i in req_list:
        if actual_day < read.requests[i]["last_day"] - 1:
            to_move_req.append(i)
        else: to_keep_req.append(i)
    return to_move_req, to_keep_req

        
#groups all the requests with respect to the due day (routes the requests as late as possible)
def assign_as_late(broute_route_schedule):
    for i in range(1, read.days + 1):
        schedule_day = broute_route_schedule[i]
        to_move_req, to_keep_req = moved_requests(schedule_day, i)
        if i != read.days and to_move_req:
            broute_route_schedule[i + 1].extend(to_move_req)
        broute_route_schedule[i] = to_keep_req
    return broute_route_schedule

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


#greedy routing algorithm starting from the brut route
#greedy routing algorithm
def creates_route_schedule(brut_route_schedule):
    route_schedule = init_route_schedules()
    check_req = [] 
    for i in range (1, read.days + 1):
        routes_list = []
        for j in range(len(brut_route_schedule[i])):
            help_list = []
            if brut_route_schedule[i][j] not in check_req:
                help_list.append(brut_route_schedule[i][j])
                check_req.append(brut_route_schedule[i][j])
                if j != len(brut_route_schedule[i]) - 1:
                    for k in range(j + 1, len(brut_route_schedule[i])):                  
                        if brut_route_schedule[i][k] not in check_req:
                            help_list.append(brut_route_schedule[i][k])
                            if get_distance(help_list) <= read.truck_max_distance and is_in_maxim_cap(help_list):
                                check_req.append(brut_route_schedule[i][k])
                            else: help_list.remove(brut_route_schedule[i][k])
                            
                        if k == len(brut_route_schedule[i]) - 1 and help_list:
                            routes_list.append(help_list)                           
                else: 
                    routes_list.append(help_list)
        route_schedule[i] = routes_list
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
    

         
        






        
        


            