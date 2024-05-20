import itertools

def possible_schedules(dataset):
    days = list(range(1, dataset.days + 1))
    schedules = []
    for r in range(1, min(dataset.days + 1, 5)):  # Limit the range of r to reduce computations
        for perm in itertools.permutations(days, r):
            if all(perm[i] < perm[i+1] for i in range(len(perm)-1)):
                if not any(perm[i+4] - perm[i] == 4 for i in range(len(perm) - 4)):  # Check for consecutive days efficiently
                    schedules.append(list(perm))
    return schedules