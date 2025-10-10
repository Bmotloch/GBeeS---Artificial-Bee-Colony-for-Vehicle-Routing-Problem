from app import MainWindow
import sys
from PyQt5.QtWidgets import QApplication
import dataGenerator
import random

if __name__ == "__main__":
    """
    for i in range(50):
        num_destinations = random.randint(5, 75)
        points = dataGenerator.generate_destinations(num_destinations, (-100, 100), (-100, 100))
        dataGenerator.save_destinations(points, f"tests\\test_{i + 1}.beetest")
    """
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
