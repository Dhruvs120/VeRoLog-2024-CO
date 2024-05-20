import numpy as np

def start_location(locations,start_location_id):
    for location in locations.values():
        if location.id == start_location_id:
            return location
    
def distance(point1, point2):
    return np.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)