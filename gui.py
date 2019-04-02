import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine

from preprocessor_manager import DataPreprocessorManager

def main():
    global app
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    engine = QQmlApplicationEngine()
    dpmanager = DataPreprocessorManager()
    engine.rootContext().setContextProperty("dpManager", dpmanager)
    engine.load('main.qml')

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
