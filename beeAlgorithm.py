import random
import dataGenerator


def fitness(route):  # fitness ktory daje jedna liczbe floata z wszystkich rozdzielen
    total = 0.0
    for path in route:
        for node in range(len(path) - 1):
            total += dataGenerator.calculate_distance(path[node], path[node + 1])
    return total


def fitness_list(route):  # fitness daje w liscie fitness dla kazdego rozdzielenia
    total = []
    for path in route:
        path_total = 0.0
        for node in range(len(path) - 1):
            path_total += dataGenerator.calculate_distance(path[node], path[node + 1])
        total.append(path_total)
    return total


def random_bees(base, points, vehicles, num_scouts):
    destinations = []
    for _ in range(num_scouts):
        destinations.append(dataGenerator.generate_solution(base, points, vehicles)[0])

    return destinations


def proximity_bees_relocate_random(route, num_workers):
    new_routes = []
    for _ in range(num_workers):
        new_route = []
        for path in route:
            new_path = path.copy()
            if len(path) > 3:
                i, j = random.sample(range(1, len(path) - 1), 2)
                node = path[i]
                new_path.remove(node)
                new_path.insert(j, node)
            new_route.append(new_path)
        new_routes.append(new_route)

    return new_routes


def proximity_bees_swap_nearby(route, num_workers):
    new_routes = []
    for _ in range(num_workers):
        new_route = []
        for path in route:
            new_path = path.copy()
            if len(path) > 3:
                i = random.randint(1, len(path) - 2)
                new_path[i], new_path[i + 1] = new_path[i + 1], new_path[i]
            new_route.append(new_path)
        new_routes.append(new_route)

    return new_routes


def proximity_bees_swap_random(route, num_workers):
    new_routes = []
    for _ in range(num_workers):
        new_route = []
        for path in route:
            new_path = path.copy()
            if len(new_path) > 4:
                i, j = random.sample(range(1, len(new_path) - 1), 2)
                new_path[i], new_path[j] = new_path[j], new_path[i]
            new_route.append(new_path)
        new_routes.append(new_route)

    return new_routes


def proximity_bees_rotate_part(route, num_workers):  # swap direction of part of the path ABCDEF -> ABEDCF
    new_routes = []
    for _ in range(num_workers):
        new_route = []
        for path in route:
            new_path = path.copy()
            if len(new_path) > 4:
                start, end = random.sample(range(1, len(new_path) - 1), 2)
                new_path[start:end] = reversed(new_path[start:end])
            new_route.append(new_path)
        new_routes.append(new_route)

    return new_routes


def bee_algorithm(
        base: (float, float),
        points: [(float, float)],
        num_iterations: int,
        vehicles=1,
        num_random=5,
        num_proximity=50,
        abandon_iterations=10,
):
    best_route, _ = dataGenerator.generate_solution(base, points, vehicles)
    best_fitness = fitness(best_route)
    fitness_epoch_list = []
    total_best_route = best_route
    total_best_fitness = best_fitness
    iteration_to_abandon = abandon_iterations

    delta1 = int(num_proximity / 4)
    delta2 = int(num_proximity / 2) - delta1
    delta3 = int(num_proximity * 3 / 4) - delta2 - delta1
    delta4 = int(num_proximity) - delta1 - delta2 - delta3

    for iteration in range(num_iterations):
        # print(f"Iteration: {iteration}")

        all_routes = (proximity_bees_swap_nearby(best_route, delta1) +
                      proximity_bees_swap_random(best_route, delta2) +
                      proximity_bees_rotate_part(best_route, delta3) +
                      proximity_bees_relocate_random(best_route, delta4) +
                      random_bees(base, points, vehicles, num_random))

        if iteration_to_abandon > 0:
            all_routes.append(best_route)

        sorted_routes_with_fitness = sorted(
            [(route, fitness(route)) for route in all_routes],
            key=lambda x: x[1]
        )

        current_best = sorted_routes_with_fitness[0][0]
        current_best_fitness = sorted_routes_with_fitness[0][1]

        if current_best_fitness < best_fitness:
            best_route = current_best
            best_fitness = current_best_fitness
            iteration_to_abandon = abandon_iterations
        else:
            iteration_to_abandon -= 1

        if best_fitness < total_best_fitness:
            total_best_route = best_route
            total_best_fitness = best_fitness

        print(f"Best route fitness at iteration {iteration}: {best_fitness}")
        fitness_epoch_list.append(best_fitness)

    return total_best_route, fitness_list(total_best_route), fitness_epoch_list
