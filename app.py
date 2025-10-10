import random
import time

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QMainWindow, QVBoxLayout, QHBoxLayout, QFileDialog, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5 import QtGui
import dataGenerator
import beeAlgorithm
import os
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class Solver(QThread):  # future VRP + Bee thread
    finished = pyqtSignal(object, object)
    error = pyqtSignal(str)

    def __init__(self, base, destinations, iterations, vehicle_num, scout_num, forager_num, abandonment_num):
        super().__init__()
        self.base = base
        self.destinations = destinations
        self.iterations = iterations
        self.vehicle_num = vehicle_num
        self.scout_num = scout_num
        self.forager_num = forager_num
        self.abandonment_num = abandonment_num
        self.routes = []
        self.distances = []
        self.fitness_epoch_list = []

    def run(self):
        try:
            self.routes, self.distances, self.fitness_epoch_list = beeAlgorithm.bee_algorithm(self.base,
                                                                        self.destinations,
                                                                        self.iterations,
                                                                        self.vehicle_num,
                                                                        self.scout_num,
                                                                        self.forager_num,
                                                                        self.abandonment_num)
            self.finished.emit(self.routes, self.distances)
        except Exception as e:
            self.error.emit(str(e))


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_xlim(-105, 105)
        self.axes.set_ylim(-105, 105)
        self.axes.grid(True)
        self.axes.set_xlabel('X')
        self.axes.set_ylabel('Y')
        self.axes.set_title('Destinations')
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.startq_time = None
        self.executionq_time = None
        self.endq_time = None
        self.solver_thread = None
        self.setWindowIcon(QtGui.QIcon('assets/icon.png'))
        self.font = QtGui.QFont("Arial", 10)
        self.test_filepath = None
        self.result_filepath = None
        self.base = None
        self.destinations = []
        self.epoch_num = 500
        self.vehicle_num = 1  # V
        self.scout_bees_num = 10  # ns
        self.forager_bees_num = 50  # nre
        self.abandonment_cycle_num = 10  # stlim

        self.routes = []
        self.bee_routes = []
        self.best_routes = []
        self.distances = []
        self.bee_distances = []
        self.best_distances = []
        self.cost = 0
        self.best_cost = 0

        self.file_button = QPushButton()
        self.file_button.setText("Choose test file")
        self.file_button.setFont(self.font)
        self.file_button.clicked.connect(self.choose_test)

        self.random_button = QPushButton()
        self.random_button.setText("Random test")
        self.random_button.setFont(self.font)
        self.random_button.clicked.connect(self.choose_random_test)

        self.reset_parameters_button = QPushButton()
        self.reset_parameters_button.setText("Reset parameters")
        self.reset_parameters_button.setFont(self.font)
        self.reset_parameters_button.clicked.connect(self.reset_parameters)

        self.generate_routes_button = QPushButton()
        self.generate_routes_button.setText("Generate initial solution")
        self.generate_routes_button.setFont(self.font)
        self.generate_routes_button.clicked.connect(self.generate_initial_solution)

        self.solve_button = QPushButton()
        self.solve_button.setText("Solve")
        self.solve_button.setFont(self.font)
        self.solve_button.hide()
        self.solve_button.clicked.connect(self.solve)

        self.save_results_button = QPushButton()
        self.save_results_button.setText("Save results")
        self.save_results_button.setFont(self.font)
        self.save_results_button.hide()
        self.save_results_button.clicked.connect(self.save_results)

        self.result_button = QPushButton()
        self.result_button.setText("Choose result file")
        self.result_button.setFont(self.font)
        self.result_button.clicked.connect(self.choose_result)

        self.epoch_label = QLabel()  # epoch
        self.epoch_label.setFont(self.font)
        self.epoch_label.setText("Epoch:")
        self.epoch_spin_box = QSpinBox()
        self.epoch_spin_box.setFont(self.font)
        self.epoch_spin_box.setEnabled(True)
        self.epoch_spin_box.setRange(1, 10000)
        self.epoch_spin_box.setValue(500)
        self.epoch_spin_box.valueChanged.connect(self.epoch_num_changed)
        self.epoch_layout = QVBoxLayout()
        self.epoch_layout.addWidget(self.epoch_label)
        self.epoch_layout.addWidget(self.epoch_spin_box)

        self.vehicle_label = QLabel()  # number of vehicles
        self.vehicle_label.setFont(self.font)
        self.vehicle_label.setText("Vehicles:")
        self.vehicle_spin_box = QSpinBox()
        self.vehicle_spin_box.setFont(self.font)
        self.vehicle_spin_box.setEnabled(True)
        self.vehicle_spin_box.setRange(1, 20)
        self.vehicle_spin_box.setValue(1)
        self.vehicle_spin_box.valueChanged.connect(self.vehicle_num_changed)
        self.vehicle_layout = QVBoxLayout()
        self.vehicle_layout.addWidget(self.vehicle_label)
        self.vehicle_layout.addWidget(self.vehicle_spin_box)

        self.scout_bees_label = QLabel()  # scout bees
        self.scout_bees_label.setFont(self.font)
        self.scout_bees_label.setText("Scout bees:")
        self.scout_bees_spin_box = QSpinBox()
        self.scout_bees_spin_box.setFont(self.font)
        self.scout_bees_spin_box.setEnabled(True)
        self.scout_bees_spin_box.setRange(1, 200)
        self.scout_bees_spin_box.setValue(50)
        self.scout_bees_spin_box.valueChanged.connect(self.scout_bees_num_changed)
        self.scout_bees_layout = QVBoxLayout()
        self.scout_bees_layout.addWidget(self.scout_bees_label)
        self.scout_bees_layout.addWidget(self.scout_bees_spin_box)

        self.forager_bees_label = QLabel()  # forager bees
        self.forager_bees_label.setFont(self.font)
        self.forager_bees_label.setText("Forager bees:")
        self.forager_bees_spin_box = QSpinBox()
        self.forager_bees_spin_box.setFont(self.font)
        self.forager_bees_spin_box.setEnabled(True)
        self.forager_bees_spin_box.setRange(1, 100)
        self.forager_bees_spin_box.setValue(50)
        self.forager_bees_spin_box.valueChanged.connect(self.forager_bees_num_changed)
        self.forager_bees_layout = QVBoxLayout()
        self.forager_bees_layout.addWidget(self.forager_bees_label)
        self.forager_bees_layout.addWidget(self.forager_bees_spin_box)

        self.abandonment_cycle_label = QLabel()  # abandonment cycle number
        self.abandonment_cycle_label.setFont(self.font)
        self.abandonment_cycle_label.setText("Abandonment cycle number:")
        self.abandonment_cycle_spin_box = QSpinBox()
        self.abandonment_cycle_spin_box.setFont(self.font)
        self.abandonment_cycle_spin_box.setEnabled(True)
        self.abandonment_cycle_spin_box.setRange(1, 100)
        self.abandonment_cycle_spin_box.setValue(10)
        self.abandonment_cycle_spin_box.valueChanged.connect(self.abandonment_cycle_num_changed)
        self.abandonment_cycle_layout = QVBoxLayout()
        self.abandonment_cycle_layout.addWidget(self.abandonment_cycle_label)
        self.abandonment_cycle_layout.addWidget(self.abandonment_cycle_spin_box)

        self.canvas = MplCanvas(self)

        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(self.font)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.file_button)
        self.button_layout.addWidget(self.random_button)
        self.button_layout.addWidget(self.reset_parameters_button)
        self.button_layout.addWidget(self.generate_routes_button)
        self.button_layout.addWidget(self.solve_button)
        self.button_layout.addWidget(self.save_results_button)
        self.button_layout.addWidget(self.result_button)
        self.button_layout.addStretch()

        self.parameters_layout = QHBoxLayout()
        self.parameters_layout.addLayout(self.epoch_layout)
        self.parameters_layout.addLayout(self.vehicle_layout)
        self.parameters_layout.addLayout(self.scout_bees_layout)
        self.parameters_layout.addLayout(self.forager_bees_layout)
        self.parameters_layout.addLayout(self.abandonment_cycle_layout)
        self.parameters_layout.addStretch()

        containerLayout = QVBoxLayout()
        containerLayout.addLayout(self.button_layout)
        containerLayout.addLayout(self.parameters_layout)
        containerLayout.addWidget(self.canvas, 1)
        containerLayout.addWidget(self.info_label)

        mainContainer = QWidget()
        mainContainer.setLayout(containerLayout)
        self.setCentralWidget(mainContainer)

        self.setGeometry(320, 180, 1280, 720)
        self.setFixedSize(1280, 720)
        self.setWindowTitle("GBeeS")

    def choose_test(self):
        file_dialog = QFileDialog(self, 'Choose test:', os.getcwd() + '\\tests\\')
        file_dialog.setNameFilter("Tests (*.beetest)")
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_():
            self.test_filepath = file_dialog.selectedFiles()[0]
            self.load_test_file()

    def choose_random_test(self):
        tests_directory = os.path.join(os.getcwd(), 'tests')
        test_files = [f for f in os.listdir(tests_directory) if f.endswith('.beetest')]
        if not test_files:
            self.print_info("No test files found in the 'tests' directory.")
            return

        while True:
            random_test_file = random.choice(test_files)
            random_test_filepath = os.path.join(tests_directory, random_test_file)

            if random_test_filepath != self.test_filepath:
                self.test_filepath = random_test_filepath
                self.load_test_file()
                break

    def load_test_file(self):
        self.base, self.destinations = dataGenerator.open_destinations(self.test_filepath)
        self.routes = []
        self.distances = []
        self.save_results_button.hide()
        self.solve_button.hide()
        if self.base is None or self.destinations is None:
            self.print_info("Test file not chosen or data not loaded.")
            return
        else:
            filename = os.path.basename(self.test_filepath)
            self.print_info(f"Loaded test: {filename}")
            self.draw_destinations()

    def choose_result(self):
        file_result = QFileDialog(self, 'Choose result:', os.getcwd() + '\\results\\')
        file_result.setNameFilter("Tests (*.beeresult)")
        file_result.setViewMode(QFileDialog.Detail)
        file_result.setFileMode(QFileDialog.ExistingFile)
        if file_result.exec_():
            self.result_filepath = file_result.selectedFiles()[0]
            self.load_result_file()


    def load_result_file(self):
        self.routes, self.distances, self.base, self.destinations = dataGenerator.open_result(self.result_filepath)
        self.save_results_button.hide()
        self.solve_button.hide()
        if self.base is None or self.destinations is None:
            self.print_info("Result file not chosen or data not loaded.")
            return
        else:
            filename = os.path.basename(self.result_filepath)
            self.print_info(f"Loaded result: {filename}")
            self.draw_destinations()
            self.draw_routes(self.routes, self.distances)
    def epoch_num_changed(self):
        self.epoch_num = self.epoch_spin_box.value()

    def vehicle_num_changed(self):
        self.vehicle_num = self.vehicle_spin_box.value()

    def scout_bees_num_changed(self):
        self.scout_bees_num = self.scout_bees_spin_box.value()

    def forager_bees_num_changed(self):
        self.forager_bees_num = self.forager_bees_spin_box.value()

    def abandonment_cycle_num_changed(self):
        self.abandonment_cycle_num = self.abandonment_cycle_spin_box.value()

    def reset_parameters(self):
        self.epoch_num = 500
        self.epoch_spin_box.setValue(500)
        self.vehicle_num = 1
        self.vehicle_spin_box.setValue(1)
        self.scout_bees_num = 50
        self.scout_bees_spin_box.setValue(50)
        self.forager_bees_num = 50
        self.forager_bees_spin_box.setValue(50)
        self.abandonment_cycle_num = 10
        self.abandonment_cycle_spin_box.setValue(10)

    def print_info(self, text):
        self.info_label.setText(text)

    def generate_initial_solution(self):
        start_time = time.time()  # Start timing
        if not self.base:
            self.print_info("No base was chosen!")
        else:
            self.routes, self.distances = dataGenerator.generate_initial_solution(self.base, self.destinations,
                                                                                  self.vehicle_num)
            self.best_routes = self.routes.copy()
            self.best_distances = self.distances.copy()
            self.draw_routes(self.routes, self.distances)
            self.cost = sum(self.distances)
            self.best_cost = self.cost
            end_time = time.time()
            execution_time = end_time - start_time
            self.print_info(f"Cost: {round(self.cost, 3)} | Time: {round(execution_time, 3)}s")
            self.solve_button.show()
            self.save_results_button.show()

    def solve(self):
        self.startq_time = time.time()  # Start timing
        self.solver_thread = Solver(self.base, self.destinations, self.epoch_num, self.vehicle_num,
                                    self.scout_bees_num, self.forager_bees_num,
                                    self.abandonment_cycle_num)
        self.solver_thread.finished.connect(self.solver_finished)
        self.solver_thread.error.connect(self.solver_error)
        self.solver_thread.start()
        self.solve_button.hide()

    def solver_finished(self, routes, distances):
        self.endq_time = time.time()  # End timing
        self.executionq_time = self.endq_time - self.startq_time
        self.bee_routes = routes
        self.bee_distances = distances
        self.compare_solutions()

    def solver_error(self, error_message):
        self.print_info(f'Error: {error_message}')

    def compare_solutions(self):
        if sum(self.bee_distances) < self.best_cost:
            self.best_cost = sum(self.bee_distances)
            self.best_routes = self.bee_routes.copy()
            self.best_distances = self.bee_distances.copy()
            self.draw_routes(self.bee_routes, self.bee_distances)
            self.cost = sum(self.bee_distances)
            self.print_info(f"Cost: {round(self.cost, 3)} | Time: {round(self.executionq_time, 3)}s")
            self.save_results_button.show()
        else:
            self.draw_routes(self.bee_routes, self.bee_distances)
            self.cost = sum(self.bee_distances)
            self.print_info(f"No cost improvement: {round(self.cost, 3)} | Time: {round(self.executionq_time, 3)}s")
            self.save_results_button.show()

    def save_results(self):
        if self.routes:
            filename = os.path.basename(self.test_filepath)
            filename = os.path.splitext(filename)[0] + ".beeresult"
            dataGenerator.save_test_results(filename, self.best_routes, self.best_distances)
            self.print_info(f"Result saved in: results\\{filename}")
            self.save_results_button.hide()

    def reset_canvas(self):
        ax = self.canvas.axes
        ax.clear()
        ax.set_xlim(-105, 105)
        ax.set_ylim(-105, 105)
        ax.grid(True)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Destinations')

    def draw_destinations(self):

        ax = self.canvas.axes
        self.reset_canvas()

        ax.plot(self.base[0], self.base[1], 'ro', markersize=10, label='Base')
        dest_x = [dest[0] for dest in self.destinations]
        dest_y = [dest[1] for dest in self.destinations]
        ax.plot(dest_x, dest_y, 'bo', markersize=7, label='Destinations')

        ax.legend()

        self.canvas.draw()

    def draw_routes(self, routes, distances):
        ax = self.canvas.axes
        self.draw_destinations()
        i = 0
        for route in routes:
            x_coordinates = [point[0] for point in route]
            y_coordinates = [point[1] for point in route]

            x_coordinates.append(route[0][0])
            y_coordinates.append(route[0][1])
            i += 1
            ax.plot(x_coordinates, y_coordinates, linestyle='--', label=f"Route {i}: {round(distances[i - 1], 3)}")
            ax.legend()
            self.canvas.draw()