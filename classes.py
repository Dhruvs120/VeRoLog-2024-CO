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
