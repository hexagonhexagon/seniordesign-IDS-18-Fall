import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine

def main():
    global app
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    engine = QQmlApplicationEngine()
    engine.load('main.qml')

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

