import os
import random
import math
import re
import ast


def generate_destinations(num_destinations, x_range, y_range):
    base_x = random.randint(x_range[0], x_range[1])
    base_y = random.randint(y_range[0], y_range[1])
    base = (base_x, base_y)  # base position

    destinations = [base]  # add base to the list
    unique_points = set()  # set is good for tracking already unique elements
    unique_points.add(base)  # add base to the set
    for _ in range(num_destinations):
        while True:  # keep creating random points
            dest_x = random.randint(x_range[0], x_range[1])
            dest_y = random.randint(y_range[0], y_range[1])
            dest_point = (dest_x, dest_y)
            if dest_point not in unique_points:  # until it is unique
                destinations.append(dest_point)
                unique_points.add(dest_point)
                break

    return destinations


def save_destinations(destinations, file_path):
    with open(file_path, 'w') as file:
        for dest in destinations:
            file.write(f"{dest[0]},{dest[1]}\n")


def open_destinations(file_path):
    destinations = []
    with open(file_path, 'r') as file:
        for line_num, line in enumerate(file):
            if line_num == 0:
                base_x, base_y = line.strip().split(',')  # reading base location
                base = (float(base_x), float(base_y))
            else:
                dest_x, dest_y = line.strip().split(',')  # reading destination points
                destinations.append((float(dest_x), float(dest_y)))
    return base, destinations


def open_result(file_path):
    with open(file_path, 'r') as file:
        pattern = r'Route: \[(.*?)\], Distance: ([\d\.]+)'
        matches = re.findall(pattern, file.read())

        routes = [ast.literal_eval(match[0]) for match in matches]
        distances = [ast.literal_eval(match[1]) for match in matches]

        if routes:
            base = routes[0][0]

        destinations = set()
        for route in routes:
            for point in route:
                destinations.add(point)
        destinations = list(destinations)
        if base in destinations:
            destinations.remove(base)

    return routes, distances, base, destinations


def save_test_results(filepath, routes, distances):
    result_directory = "results"
    if not os.path.exists(result_directory):
        os.makedirs(result_directory)

    filepath = os.path.join(result_directory, filepath)
    with open(filepath, 'w') as file:
        for route, distance in zip(routes, distances):
            file.write(f"Route: {route}, Distance: {distance}\n")
        file.write(f"Total Distance: {sum(distances)}\n")


def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def find_nearest_neighbor(current_point, unvisited):
    min_distance = float('inf')
    nearest_point = None
    for point_idx in unvisited:
        dist = calculate_distance(current_point, point_idx)
        if dist < min_distance:
            min_distance = dist
            nearest_point = point_idx
    return nearest_point, min_distance


def generate_initial_solution(base, destinations, vehicle_num):
    generate_edges_list(base, destinations)
    unvisited = destinations.copy()
    routes = [[] for _ in range(vehicle_num)]

    distances = [0 for _ in range(vehicle_num)]

    for vehicle in range(vehicle_num):
        routes[vehicle].append(base)

    while unvisited:
        for vehicle in range(vehicle_num):
            current_point = routes[vehicle][-1]
            nearest_point, min_distance = find_nearest_neighbor(current_point, unvisited)
            routes[vehicle].append(nearest_point)
            distances[vehicle] += min_distance
            unvisited.remove(nearest_point)
            if not unvisited:
                break

    for vehicle in range(vehicle_num):
        routes[vehicle].append(base)
        distances[vehicle] += calculate_distance(routes[vehicle][-2], base)

    return routes, distances


def generate_edges_list(base, destinations):
    edges = []

    for destination in destinations:
        edges.append([base, destination])

    for i in range(len(destinations)):
        for j in range(i + 1, len(destinations)):
            edges.append([destinations[i], destinations[j]])
    return edges


def angle_with_starting_edge(starting_edge, point):
    base = starting_edge[0]
    return math.atan2(point[1] - base[1], point[0] - base[0])


def calculate_route_distance(route):
    return sum(calculate_distance(route[i], route[i + 1]) for i in range(len(route) - 1))


def generate_solution(base, destinations, vehicle_num):
    edges = generate_edges_list(base, destinations)
    distances = [0 for _ in range(vehicle_num)]
    routes = [[] for _ in range(vehicle_num)]

    average_load = len(destinations) // vehicle_num  # default destinations per route
    leftovers = len(destinations) % vehicle_num  # leftovers destinations to distribute across routes
    load_list = [average_load + 1 if i < leftovers else average_load for i in
                 range(vehicle_num)]  # destinations per vehicle
    random.shuffle(load_list)  # randomisation no. 1

    starting_edges = [edge for edge in edges if
                      (edge[0] == base and edge[1] in destinations)]  # take only base-dest edges
    starting_edge = random.choice(starting_edges)  # randomisation no. 2, first line

    unvisited = destinations.copy()  # keeping track of destinations left
    for vehicle in range(vehicle_num):
        routes[vehicle].append(base)

    clockwise = random.choice([True, False])  # randomisation no. 3, clockwise, anticlockwise

    vehicle_idx = 0
    while unvisited:
        # sort by smallest angle
        if clockwise:
            unvisited.sort(key=lambda x: angle_with_starting_edge(starting_edge, x))
        else:
            unvisited.sort(key=lambda x: -angle_with_starting_edge(starting_edge, x))

        for load in load_list:
            if not unvisited:
                break
            current_load = 0
            while current_load < load:
                next_destination = unvisited.pop(0)
                routes[vehicle_idx].append(next_destination)
                distances[vehicle_idx] += calculate_distance(routes[vehicle_idx][-2], next_destination)
                current_load += 1
                if current_load == load:
                    distances[vehicle_idx] += calculate_distance(next_destination, base)
                    routes[vehicle_idx].append(base)
                    vehicle_idx += 1  # move to the next vehicle
                    break

    for vehicle_idx in range(vehicle_num):
        route = routes[vehicle_idx]
        original_distance = distances[vehicle_idx]

        if len(route) > 3:
            swapped = False
            i = 1
            indices = list(range(1, len(route) - 2))  # excluding base point
            random.shuffle(indices)  # randomisation no. 4 + cost improvement
            for i in indices:
                route[i], route[i + 1] = route[i + 1], route[i]
                new_distance = calculate_route_distance(route)

                if new_distance < original_distance:
                    distances[vehicle_idx] = new_distance
                    swapped = True
                    break  # only one pair swap per route

                route[i], route[i + 1] = route[i + 1], route[i]

            if not swapped and len(route) > 4:
                route[i], route[i + 1] = route[i + 1], route[i]

    return routes, distances
