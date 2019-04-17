from gui.two_stage_ids_manager import TwoStageIDSManager
from ids.malicious import MaliciousGenerator
import ids.preprocessor as dp

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QVariant, QUrl
from PyQt5.QtQml import QJSValue

import os

savedata_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../savedata'
idprobs_dir = savedata_dir + '/idprobs'

class SimulationManager(QObject):
    def __init__(self, ids_manager: TwoStageIDSManager):
        # Required line for anything that inherits from QObject.
        QObject.__init__(self)

        self._ids_manager = ids_manager
        self._malgen = MaliciousGenerator()
        self._current_canlist = []
        self._current_labels = []

    result = pyqtSignal(QVariant)
    simDone = pyqtSignal()

    @pyqtSlot(QJSValue)
    def adjust_malgen(self, adjustments):
        self._malgen.adjust(adjustments)

    @pyqtSlot()
    def judge_next_frame(self):
        if self._current_canlist:
            if len(self._current_canlist) > 1:
                next_frame = self._current_canlist[1]
                self._current_canlist.pop(0)
                next_label = self._current_labels[1]
                self._current_labels.pop(0)
            else:
                next_frame = self._current_canlist.pop(0)
                next_label = self._current_labels.pop(0)
            judgement_result = self._ids_manager.judge_single_frame(next_frame)

            self.result.emit({
                'Frame': next_frame,
                'Label': next_label,
                'Judgement': judgement_result[0],
                'Reason': judgement_result[1]
            })
        else:
            self.stop_simulation()

    @pyqtSlot(QVariant, str)
    def start_simulation(self, can_file_url, idprobs_name):
        file_path = can_file_url.toString()[7:]
        if file_path.endswith('.traffic'):
            canlist = dp.parse_traffic(file_path)
        elif file_path.endswith('.csv'):
            canlist = dp.parse_csv(file_path)
        elif file_path.endswith('.json'):
            canlist = dp.load_canlist(file_path)
        else:
            raise ValueError(f'Unknown type of CAN frame file provided: {file_path}.')
        self._current_canlist, self._current_labels = dp.inject_malicious_packets(canlist, self._malgen)

        self._ids_manager._ids.change_ids_parameters('idprobs_path', idprobs_dir + '/' + idprobs_name + '.json')
        self._ids_manager.start_simulation()

    @pyqtSlot(str)
    def inject_malicious_packet(self, attack_name):
        if len(self._current_canlist > 1):
            malicious_frames, malicious_labels = self._malgen.get_attack(
                (self._current_canlist[0], self._current_canlist[1]),
                attack_name
            )
            self._current_canlist = malicious_frames + self._current_canlist
            self._current_labels = malicious_labels + self._current_labels

    @pyqtSlot()
    def stop_simulation(self):
        self._ids_manager.stop_simulation()
        self.simDone.emit()