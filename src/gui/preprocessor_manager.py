import ids.preprocessor as dp
from ids.malicious import MaliciousGenerator

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QVariant, QUrl
from PyQt5.QtQml import QJSValue
import os
import platform

# Set up directories the Data Preprocessor uses.
savedata_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../savedata'
idprobs_dir = savedata_dir + '/idprobs'
datasets_dir = savedata_dir + '/datasets'

# Inherits from QObject, which is what allows it to be used in QML.
class DataPreprocessorManager(QObject):
    def __init__(self):
        # Required line for anything that inherits from QObject.
        QObject.__init__(self)

        # Enumerate all available ID probabilities file names (without the
        # extension).
        self._available_idprobs = []
        for filename in os.listdir(idprobs_dir):
            if filename != '.gitignore':
                self._available_idprobs.append(filename.replace('.json', ''))

        # Enumerate all available dataset names.
        self._available_datasets = []
        for dirname in os.listdir(datasets_dir):
            if dirname != '.gitignore':
                self._available_datasets.append(dirname)

    # Set up availableIdprobs property. Must have @pyqtProperty decorator in
    # order to be visible to QML, where type must be specified. QVariant is a
    # catch-all type for any type that does not fit into a bool, str, int, or
    # float. Any proerty that can change must have the notify signal specified,
    # and the signal must be emitted when it does change. See
    # https://www.riverbankcomputing.com/static/Docs/PyQt5/qt_properties.html
    # for more details.
    get_availableIdprobs = pyqtSignal()

    @pyqtProperty(QVariant, notify=get_availableIdprobs)
    def availableIdprobs(self):
        return self._available_idprobs

    # Set up availableDatasets property.
    get_availableDatasets = pyqtSignal()

    @pyqtProperty(QVariant, notify=get_availableDatasets)
    def availableDatasets(self):
        return self._available_datasets

    # Set up creation of ID probabilities file. Must have @pyqtSlot decorator in
    # order to be visible to QML, and one must specify the types of the
    # arguments. Here, list_of_can_files is a list of QUrl objects.
    @pyqtSlot(QVariant, str)
    def create_idprobs_file(self, list_of_can_files, idprobs_name):
        canlist = []
        # Here, each entry in `list_of_can_files` is a QUrl.
        for file_url in list_of_can_files:
            # toString() returns 'file://<actual file path>', so strip the
            # beginning and open the rest.
            if platform.system() == 'Windows':
                file_path = file_url.toString()[8:]
            else:
                file_path = file_url.toString()[7:]
            if file_path.endswith('.traffic'):
                canlist += dp.parse_traffic(file_path)
            elif file_path.endswith('.csv'):
                canlist += dp.parse_csv(file_path)
            elif file_path.endswith('.json'):
                canlist += dp.load_canlist(file_path)
            else:
                raise ValueError(f'Unknown type of CAN frame file provided: {file_path}.')
        dp.write_id_probs(canlist, idprobs_dir + '/' + idprobs_name + '.json')
        # After writing the file, update the available ID probs files by
        # appending to the list and then emitting the "notify" signal.
        self._available_idprobs.append(idprobs_name)
        self.get_availableIdprobs.emit()

    # Set up creation of a dataset, which involves writing the good CAN frame
    # file, CAN frame file with malicious frames injected, and the feature lists
    # and labels. Here, can_file_url is a QUrl and malgen_probs is a JS object,
    # as that is how it is passed in from the GUI.
    @pyqtSlot(QVariant, str, QJSValue, str)
    def create_dataset(self, can_file_url, idprobs_name, malgen_probs, dataset_name):
        # Convert the JS object to a dictionary.
        malgen_probs = malgen_probs.toVariant()
        if platform.system() == 'Windows':
            file_path = can_file_url.toString()[8:]
        else:
            file_path = can_file_url.toString()[7:]
        if file_path.endswith('.traffic'):
            canlist = dp.parse_traffic(file_path)
        elif file_path.endswith('.csv'):
            canlist = dp.parse_csv(file_path)
        elif file_path.endswith('.json'):
            canlist = dp.load_canlist(file_path)
        else:
            raise ValueError(f'Unknown type of CAN frame file provided: {file_path}.')

        idprobs = dp.load_id_probs(idprobs_dir + '/' + idprobs_name + '.json')

        # Create a folder under the 'datasets' folder with the name being the
        # name of the dataset. This is where all the relevant files for the
        # dataset go.
        dataset_folder = datasets_dir + '/' + dataset_name
        os.mkdir(dataset_folder)
        # Write the good CAN frame file.
        dp.write_canlist(canlist, dataset_folder + '/good_canlist.json')

        # Create the CAN frame file with malicious frames injected.
        malgen = MaliciousGenerator()
        malgen.adjust(malgen_probs)
        bad_canlist, labels = dp.inject_malicious_packets(canlist, malgen)
        dp.write_canlist(bad_canlist, dataset_folder + '/bad_canlist.json')

        # Create the feature lists/labels file.
        features = dp.generate_feature_lists(bad_canlist, idprobs)
        dp.write_feature_lists(features, labels, dataset_folder + '/features_labels.json')
        # Update the available datasets.
        self._available_datasets.append(dataset_name)
        self.get_availableDatasets.emit()
