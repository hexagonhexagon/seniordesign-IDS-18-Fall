from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QVariant, QUrl
from PyQt5.QtQml import QJSValue

# We will occasionally divide 0/0, in which case we want to return 0.
def safe_div(num1, num2):
    if num1 == 0 and num2 == 0:
        return 0.0
    else:
        # There will never be a case where we divide <nonzero>/0, so this is safe.
        return num1 / num2

class ReportManager(QObject):
    def __init__(self):
        # Required line for anything that inherits from QObject.
        QObject.__init__(self)

        self._statistics = {
            'total': 0,
            'total_benign': 0,
            'total_malicious': 0,
            'true_positive': 0,
            'true_negative': 0,
            'false_positive': 0,
            'false_negative': 0,
            'random': {
                'total': 0,
                'true_positive': 0
            },
            'replay': {
                'total': 0,
                'true_positive': 0
            },
            'flood': {
                'total': 0,
                'true_positive': 0
            },
            'spoof': {
                'total': 0,
                'true_positive': 0
            }
        }

    get_statistics = pyqtSignal()

    @pyqtProperty(QVariant, notify=get_statistics)
    def statistics(self):
        stats = self._statistics
        precision = safe_div(stats['true_positive'], stats['true_positive'] + stats['false_positive'])
        recall = safe_div(stats['true_positive'], stats['total_malicious'])
        return [
            {
                'stat': 'Accuracy',
                'value': safe_div(stats['true_positive'] + stats['true_negative'], stats['total'])
            },
            {
                'stat': 'Benign Passed',
                'value': safe_div(stats['true_negative'], stats['total_benign'])
            },
            {
                'stat': 'Malicious Caught',
                'value': safe_div(stats['true_positive'], stats['total_malicious'])
            },
            {
                'stat': 'False Positives',
                'value': safe_div(stats['false_positive'], stats['total_benign'])
            },
            {
                'stat': 'False Negatives',
                'value': safe_div(stats['false_negative'], stats['total_malicious'])
            },
            {
                'stat': 'Random Attack Caught',
                'value': safe_div(stats['random']['true_positive'], stats['random']['total'])
            },
            {
                'stat': 'Replay Attack Caught',
                'value': safe_div(stats['replay']['true_positive'], stats['replay']['total'])
            },
            {
                'stat': 'DoS Attack Caught',
                'value': safe_div(stats['flood']['true_positive'], stats['flood']['total'])
            },
            {
                'stat': 'Spoofing Attack Caught',
                'value': safe_div(stats['spoof']['true_positive'], stats['spoof']['total'])
            },
            {
                'stat': 'F1 Score',
                'value': safe_div(2 * precision * recall, precision + recall)
            }
        ]

    @pyqtSlot()
    def reset_statistics(self):
        for key in self._statistics.keys():
            if isinstance(self._statistics[key], dict):
                for sub_key in self._statistics[key]:
                    self._statistics[key][sub_key] = 0
            else:
                self._statistics[key] = 0
        self.get_statistics.emit()

    @pyqtSlot(QJSValue)
    def update_statistics(self, judgement_result):
        judgement_result = judgement_result.toVariant()

        self._statistics['total'] += 1

        label = judgement_result['Label']
        is_malicious = bool(label) # False if label == None, True otherwise.
        if is_malicious:
            self._statistics['total_malicious'] += 1
            self._statistics[label]['total'] += 1
        else:
            self._statistics['total_benign'] += 1

        judge_malicious = judgement_result['Judgement']
        if not is_malicious and not judge_malicious:
            self._statistics['true_negative'] += 1
        elif is_malicious and judge_malicious:
            self._statistics['true_positive'] += 1
            self._statistics[label]['true_positive'] += 1
        elif not is_malicious and judge_malicious:
            self._statistics['false_positive'] += 1
        elif is_malicious and not judge_malicious:
            self._statistics['false_negative'] += 1

        self.get_statistics.emit()