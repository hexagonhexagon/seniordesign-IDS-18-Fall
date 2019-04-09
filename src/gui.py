import sys
import os.path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine

from gui.preprocessor_manager import DataPreprocessorManager

def main():
    global app
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    engine = QQmlApplicationEngine()
    dpmanager = DataPreprocessorManager()
    engine.rootContext().setContextProperty("dpManager", dpmanager)
    engine.load(os.path.dirname(os.path.abspath(__file__)) + '/gui/main.qml')

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
