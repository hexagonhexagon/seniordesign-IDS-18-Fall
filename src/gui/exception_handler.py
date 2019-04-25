from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QVariant, QUrl
from PyQt5.QtQml import QJSValue

import traceback

class ExceptionHandler(QObject):
    def __init__(self):
        QObject.__init__(self)

    handledException = pyqtSignal(str)
    unhandledException = pyqtSignal(QVariant)

    def handle_exception(self, exc):
        self.handledException.emit(exc.args[0])

    def excepthook(self, exctype, value, tb):
        exception_text = f'{exctype.__name__}: {value.args[0]}'
        traceback_text = ''.join(traceback.format_tb(tb))
        self.unhandledException.emit({
            'error': exception_text,
            'traceback': traceback_text
        })

excHandler = ExceptionHandler()