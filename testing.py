import time
import numpy as np
import app
import dataGenerator
import os


def run_algorithm(base, destinations, epoch_num, vehicle_num, scout_bees_num, forager_bees_num, abandonment_cycle_num):
    solver_thread = app.Solver(base, destinations, epoch_num, vehicle_num, scout_bees_num, forager_bees_num,
                               abandonment_cycle_num)
    start_time = time.time()
    solver_thread.run()
    end_time = time.time()
    execution_time = end_time - start_time
    return solver_thread.routes, solver_thread.distances, solver_thread.fitness_epoch_list, execution_time


def test_parameters(base, destinations, epoch_num, vehicle_num, scout_bees_num, forager_bees_num, abandonment_cycle_num,
                    num_runs):
    times = []
    results = []
    fitness_all_runs = []

    for _ in range(num_runs):
        routes, distances, fitness, execution_time = run_algorithm(base, destinations, epoch_num, vehicle_num,
                                                                   scout_bees_num, forager_bees_num,
                                                                   abandonment_cycle_num)
        times.append(execution_time)
        results.append(distances)
        fitness_all_runs.append(fitness)

    average_time = np.mean(times)
    std_dev_time = np.std(times)
    average_result = np.mean(results, axis=0)
    std_dev_result = np.std(results, axis=0)

    # Average fitness across epochs for all runs
    average_fitness = np.mean(fitness_all_runs, axis=0)
    std_dev_fitness = np.std(fitness_all_runs, axis=0)

    return average_time, std_dev_time, average_result, std_dev_result, average_fitness, std_dev_fitness


def create_report_filename(test_num, epoch_num, vehicle_num, scout_bees_num, forager_bees_num, abandonment_cycle_num,
                           num_runs):
    filename = f"report_test{test_num}_epochs{epoch_num}_vehicles{vehicle_num}_scout{scout_bees_num}_forager{forager_bees_num}_abandon{abandonment_cycle_num}_runs{num_runs}.txt"
    return filename


def save_report(filepath, test_num, epoch_num, vehicle_num, scout_bees_num, forager_bees_num, abandonment_cycle_num,
                num_runs,
                average_time, std_dev_time, average_result, std_dev_result, average_fitness, std_dev_fitness):
    with open(filepath, 'w') as file:
        file.write("Algorithm Performance Report\n")
        file.write("============================\n\n")
        file.write(f"Test number: {test_num}\n")
        file.write(f"Epochs: {epoch_num}\n")
        file.write(f"Number of vehicles: {vehicle_num}\n")
        file.write(f"Number of scout bees: {scout_bees_num}\n")
        file.write(f"Number of forager bees: {forager_bees_num}\n")
        file.write(f"Abandonment cycle number: {abandonment_cycle_num}\n")
        file.write(f"Number of runs: {num_runs}\n\n")
        file.write(f"Average execution time: {average_time} seconds\n")
        file.write(f"Standard deviation of execution time: {std_dev_time}\n\n")
        file.write(f"Average result: {average_result}\n")
        file.write(f"Standard deviation of result: {std_dev_result}\n\n")
        file.write(f"Average total cost: {average_result.sum()}\n\n")
        file.write("Average fitness per epoch:\n")
        for epoch, (avg_fit, std_dev_fit) in enumerate(zip(average_fitness, std_dev_fitness)):
            file.write(f"Epoch {epoch + 1}: {avg_fit} (std dev: {std_dev_fit})\n")


test_filepath = 'tests\\test_51.beetest'

# Extract test number from file path
test_num = test_filepath.split('_')[1].split('.')[0]

base, destinations = dataGenerator.open_destinations(test_filepath)
epoch_num = 1000
vehicle_num = 5
scout_bees_num = 50
forager_bees_num = 50
abandonment_cycle_num = 100
num_runs = 10

average_time, std_dev_time, average_result, std_dev_result, average_fitness, std_dev_fitness = test_parameters(
    base, destinations, epoch_num, vehicle_num, scout_bees_num, forager_bees_num, abandonment_cycle_num, num_runs)

print(f"Average execution time: {average_time} seconds (std dev: {std_dev_time})")
print(f"Average result: {average_result} (std dev: {std_dev_result})")
print("Average fitness per epoch:")
for epoch, (avg_fit, std_dev_fit) in enumerate(zip(average_fitness, std_dev_fitness)):
    print(f"Epoch {epoch + 1}: {avg_fit} (std dev: {std_dev_fit})")

report_folder = 'reports'
os.makedirs(report_folder, exist_ok=True)
report_filename = create_report_filename(test_num, epoch_num, vehicle_num, scout_bees_num, forager_bees_num,
                                         abandonment_cycle_num, 10)
report_filepath = os.path.join(report_folder, report_filename)

save_report(report_filepath, test_num, epoch_num, vehicle_num, scout_bees_num, forager_bees_num, abandonment_cycle_num,
            10,
            average_time, std_dev_time, average_result, std_dev_result, average_fitness, std_dev_fitness)
print(f"Report saved to {report_filepath}")
