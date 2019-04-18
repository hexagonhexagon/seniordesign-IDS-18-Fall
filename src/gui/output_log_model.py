from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QVariant, QSortFilterProxyModel, QModelIndex, QAbstractListModel, Qt
from PyQt5.QtQml import QJSValue

# Based off of https://github.com/baoboa/pyqt5/tree/master/examples/quick/models/abstractitemmodel
class BaseOutputLogModel(QAbstractListModel):
    FrameRole = Qt.UserRole + 1
    LabelRole = Qt.UserRole + 2
    JudgementRole = Qt.UserRole + 3
    ReasonRole = Qt.UserRole + 4

    _roles = {
        FrameRole: b'frame',
        LabelRole: b'label',
        JudgementRole: b'judgement',
        ReasonRole: b'reason'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._judgements = []

    def append(self, judgement):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._judgements.append(judgement)
        self.endInsertRows()

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self._judgements = []
        self.endRemoveRows()

    def rowCount(self, parent=QModelIndex()):
        return len(self._judgements)

    def data(self, index, role=Qt.DisplayRole):
        try:
            judgement = self._judgements[index.row()]
        except IndexError:
            return QVariant()

        if role == self.FrameRole:
            return judgement['Frame']
        elif role == self.LabelRole:
            label = judgement['Label']
            if not label:
                return 'benign'
            else:
                return label
        elif role == self.JudgementRole:
            return judgement['Judgement']
        elif role == self.ReasonRole:
            reason = judgement['Reason']
            if isinstance(reason, float):
                return f'DNN Based IDS (confidence {reason})'
            elif isinstance(reason, str):
                return f'Rules Based IDS ({reason} rule)'
            else:
                return QVariant()
        else:
            return QVariant()

    def roleNames(self):
        return self._roles

class OutputLogModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filters = {
            'true_positive': True,
            'true_negative': True,
            'false_positive': True,
            'false_negative': True,
            'benign': True,
            'random': True,
            'replay': True,
            'spoof': True,
            'flood': True
        }

    @pyqtSlot(str, bool)
    def change_filter(self, filter_name, value):
        self._filters[filter_name] = value
        self.invalidateFilter()

    @pyqtSlot(QJSValue)
    def append(self, judgement):
        self.sourceModel().append(judgement.toVariant())

    @pyqtSlot()
    def clear(self):
        self.sourceModel().clear()

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        label = self.sourceModel().data(index, BaseOutputLogModel.LabelRole)
        if not label:
            label = 'benign'
        # This type of attack is disabled in the log.
        if not self._filters[label]:
            return False

        is_malicious = (label != 'benign')
        judgement = self.sourceModel().data(index, BaseOutputLogModel.JudgementRole)
        # This type of result is disabled in the log
        if not is_malicious and not judgement:
            return self._filters['true_negative']
        elif is_malicious and judgement:
            return self._filters['true_positive']
        elif not is_malicious and judgement:
            return self._filters['false_positive']
        elif is_malicious and not judgement:
            return self._filters['false_negative']
