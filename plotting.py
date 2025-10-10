import matplotlib.pyplot as plt
import re
import os


def read_report(filepath):
    data = {}
    with open(filepath, 'r') as file:
        lines = file.readlines()
        data['Test number'] = int(lines[3].split(': ')[1].strip())
        data['Epochs'] = int(lines[4].split(': ')[1].strip())
        data['Number of vehicles'] = int(lines[5].split(': ')[1].strip())
        data['Number of scout bees'] = int(lines[6].split(': ')[1].strip())
        data['Number of forager bees'] = int(lines[7].split(': ')[1].strip())
        data['Abandonment cycle number'] = int(lines[8].split(': ')[1].strip())
        data['Number of runs'] = int(lines[9].split(': ')[1].strip())
        data['Average execution time'] = float(lines[11].split(': ')[1].split(' ')[0].strip())
        data['Standard deviation of execution time'] = float(lines[12].split(': ')[1].strip())
        data['Average total cost'] = float(lines[17].split(': ')[1].strip())
        # Extract average fitness per epoch
        epoch_fitness = {}
        for line in lines[20:]:
            match = re.match(r'Epoch (\d+): ([\d.]+) \(std dev: ([\d.]+)\)', line)
            if match:
                epoch_number = int(match.group(1))
                average_fitness = float(match.group(2))
                std_dev_fitness = float(match.group(3))
                epoch_fitness[epoch_number] = {'Average': average_fitness, 'Standard deviation': std_dev_fitness}
        data['Average fitness per epoch'] = epoch_fitness
    return data


def plot_execution_time():
    parameter_num = [10, 20, 30, 50, 100]
    avg_execution_time = [278.63905506134034, 285.26783215999603, 275.5273118019104, 268.37529933452606,
                          272.70075929164886]
    std_execution_time = [7.174528563703968, 4.587832093238831, 5.3179285526275635, 2.5065046548843384,
                          2.541478991508484]

    plt.errorbar(parameter_num, avg_execution_time, yerr=std_execution_time, fmt='o', markersize=8, capsize=5,
                 capthick=2, linewidth=2)
    plt.title('Average Execution Time', fontsize=16)
    plt.xlabel('Abandonment Cycle Number', fontsize=14)
    plt.ylabel('Time (seconds)', fontsize=14)
    plt.xticks(parameter_num, fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()


def plot_fitness(data, filepath):
    basename = os.path.basename(filepath)
    epochs = list(data['Average fitness per epoch'].keys())
    avg_fitness = [value['Average'] for value in data['Average fitness per epoch'].values()]
    std_fitness = [value['Standard deviation'] for value in data['Average fitness per epoch'].values()]

    test_num = data['Test number']
    epochs_num = data['Epochs']
    vehicle_num = data['Number of vehicles']
    scout_bees_num = data['Number of scout bees']
    forager_bees_num = data['Number of forager bees']
    abandonment_cycle_num = data['Abandonment cycle number']

    plt.figure(figsize=(10, 5))

    plt.plot(epochs, avg_fitness, '-', label='Average Fitness', linewidth=2)

    plt.fill_between(epochs, [avg - std for avg, std in zip(avg_fitness, std_fitness)],
                     [avg + std for avg, std in zip(avg_fitness, std_fitness)], color='lightgrey',
                     label='Standard Deviation')

    plt.title(
        f'Average Fitness per Epoch\nTest Number: {test_num}, Epochs: {epochs_num}, Vehicles: {vehicle_num}, Scout Bees: {scout_bees_num}, Forager Bees: {forager_bees_num}, Abandonment Cycles: {abandonment_cycle_num}')
    plt.xlabel('Epoch')
    plt.ylabel('Fitness')
    plt.grid(True)
    plt.legend()
    plt.savefig(f'plots//{basename}.png')
    # plt.show()


# report_filepath = 'reports//report_test51_epochs1000_vehicles5_scout50_forager50_abandon100_runs10.txt'
# report_data = read_report(report_filepath)

# plot_fitness(report_data, report_filepath)
plot_execution_time()
