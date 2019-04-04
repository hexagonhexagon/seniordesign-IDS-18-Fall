import ids.preprocessor as dp
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QVariant, QUrl

class DataPreprocessorManager(QObject):
    def __init__(self):
        QObject.__init__(self)

    @pyqtSlot(QVariant, str)
    def create_idprobs_file(self, list_of_can_files, idprobs_name):
        canlist = []
        for file_url in list_of_can_files:
            file_path = file_url.toString()[7:]
            if file_path.endswith('.traffic'):
                canlist += dp.parse_traffic(file_path)
            elif file_path.endswith('.csv'):
                canlist += dp.parse_csv(file_path)
            elif file_path.endswith('.json'):
                canlist += dp.load_canlist(file_path)
            else:
                raise ValueError(f'Unknown type of CAN frame file provided: {file_path}.')
        dp.write_id_probs(canlist, './savedata/idprobs/' + idprobs_name + '.json')


    @pyqtSlot(str, str)
    def create_dataset(self, can_file, idprobs_name):
        pass