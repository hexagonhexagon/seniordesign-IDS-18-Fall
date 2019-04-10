import sys
import os.path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine

from gui.preprocessor_manager import DataPreprocessorManager

def main():
    global app
    # The following command line argument sets the style of the QML app. There is no alternative.
    # Available styles: https://doc.qt.io/qt-5/qtquickcontrols2-styles.html
    sys.argv += ['--style', 'fusion']
    app = QApplication(sys.argv)

    # Make the Data Preprocessor Manager accessible through QML.
    engine = QQmlApplicationEngine()
    dpmanager = DataPreprocessorManager()
    engine.rootContext().setContextProperty("dpManager", dpmanager)
    # Load the QML file.
    engine.load(os.path.dirname(os.path.abspath(__file__)) + '/gui/main.qml')

    # Run the QML file.
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
