from partFunctions import start_location, distance
import itertools


def find_routes(start_location_id, max_distance,locations):
    # Filter locations to include only those with ID not equal to start_location_id
    destinations = []
    routes = []

    for loc in locations.values():
        if loc.id != start_location_id:
            destinations.append(loc)
    
    # Generate all possible permutations of destinations
    for r in range(1, len(destinations) + 1):
        for perm in itertools.permutations(destinations, r):
            route = [start_location(locations, start_location_id)] + list(perm) + [start_location(locations, start_location_id)]
            total_distance = sum(distance(route[i], route[i+1]) for i in range(0,len(route)-1))
            if total_distance <= max_distance:
                routes.append([route,total_distance])
    return routes
