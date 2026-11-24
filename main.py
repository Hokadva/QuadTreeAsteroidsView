"""Main file"""
import sys

from PyQt6.QtWidgets import QApplication # pylint: disable=E0611

from modules.asteroids import AsteroidManager
from modules.consts import CAPACITY, base_settings
from modules.ui import UI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    asteroid_manager = AsteroidManager(**base_settings, capacity=CAPACITY)
    window = UI(asteroid_manager)
    window.show()
    sys.exit(app.exec())
