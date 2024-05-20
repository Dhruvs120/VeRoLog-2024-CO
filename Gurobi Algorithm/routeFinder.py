import itertools
from partFunctions import distance, start_location

def find_routes(start_location_id, max_distance, locations):
    
    # Filter locations to include only those with ID not equal to start_location_id
    destinations = [loc for loc in locations.values() if loc.id != start_location_id]
    routes = []
    
    if len(destinations) > 4:
        number_of_destinations = 4
    else:
        number_of_destinations = len(destinations)
    # Generate all possible subsets of destinations
    for r in range(1, number_of_destinations):
        for subset in itertools.combinations(destinations, r):
            # Generate permutations of the subset
            for perm in itertools.permutations(subset):
                sorted_perm = tuple(sorted(perm, key=lambda loc: loc.id))
                if routes and routes[-1][0][1:-1] == sorted_perm:
                    continue
                route = [start_location(locations, start_location_id)] + list(sorted_perm) + [start_location(locations, start_location_id)]
                total_distance = sum(distance(route[i], route[i+1]) for i in range(len(route) - 1))
                if total_distance <= max_distance:
                    routes.append((route, total_distance))
    return routes