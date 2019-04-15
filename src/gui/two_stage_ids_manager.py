from ids.two_stage_ids import TwoStageIDS
import ids.preprocessor as dp
from ids.dnn_ids import dnn_input_function

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QVariant, QUrl
from PyQt5.QtQml import QJSValue
import os
import shutil
import tensorflow as tf
from ast import literal_eval

# Set up directories.
savedata_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../savedata'
dnnmodels_dir = savedata_dir + '/dnn-models'
ruleprofiles_dir = savedata_dir + '/rule-profiles'
idprobs_dir = savedata_dir + '/idprobs'
datasets_dir = savedata_dir + '/datasets'

# Set up object -> name correspondences.
activation_fn_convert = {
    tf.nn.relu: "ReLU",
    tf.nn.relu6: "ReLU 6",
    tf.nn.crelu: "CReLU",
    tf.nn.elu: "ELU",
    tf.nn.selu: "SELU",
    tf.nn.softplus: "Softplus",
    tf.nn.softsign: "Softsign",
    tf.sigmoid: "Sigmoid",
    tf.tanh: "Tanh"
}

activation_fn_convert_reverse = {v: k for k, v in activation_fn_convert.items()}

loss_reduction_convert = {
    tf.losses.Reduction.NONE: "None",
    tf.losses.Reduction.MEAN: "Mean",
    tf.losses.Reduction.SUM: "Sum",
    tf.losses.Reduction.SUM_OVER_BATCH_SIZE: "Sum over Batch Size",
    tf.losses.Reduction.SUM_OVER_NONZERO_WEIGHTS: "Sum over Nonzero Weights",
    tf.losses.Reduction.SUM_BY_NONZERO_WEIGHTS: "Sum by Nonzero Weights"
}

loss_reduction_convert_reverse = {v: k for k, v in loss_reduction_convert.items()}

optimizer_convert = {
    tf.train.AdadeltaOptimizer: "Adadelta Optimizer",
    tf.train.AdagradDAOptimizer: "Adagrad DA Optimizer",
    tf.train.AdagradOptimizer: "Adagrad Optimizer",
    tf.train.AdamOptimizer: "Adam Optimizer",
    tf.train.FtrlOptimizer: "FTRL Optimizer",
    tf.train.GradientDescentOptimizer: "Gradient Descent Optimizer",
    tf.train.MomentumOptimizer: "Momentum Optimizer",
    tf.train.ProximalAdagradOptimizer: "Proximal Adagrad Optimizer",
    tf.train.ProximalGradientDescentOptimizer: "Proximal Gradient Descent Optimizer",
    tf.train.RMSPropOptimizer: "RMS Prop Optimizer"
}

optimizer_convert_reverse = {v: k for k, v in optimizer_convert.items()}

# Inherits from QObject, which is what allows it to be used in QML.
class TwoStageIDSManager(QObject):
    def __init__(self):
        # Required line for anything that inherits from QObject.
        QObject.__init__(self)

        self._ids = TwoStageIDS()
        # Enumerate all available Two Stage IDS models.
        self._available_models = []
        for file_or_dirname in os.listdir(dnnmodels_dir):
            if file_or_dirname.endswith('.params'):
                self._available_models.append(file_or_dirname.replace('.params', ''))

        self._model_name = ''

    # List of all Two Stage IDS models.
    get_availableModels = pyqtSignal()

    @pyqtProperty(QVariant, notify=get_availableModels)
    def availableModels(self):
        return self._available_models

    # Transform internal properties of the IDS into a form the GUI can
    # understand.
    get_parameters = pyqtSignal()

    @pyqtProperty(QVariant, notify=get_parameters)
    def parameters(self):
        if self._model_name:
            return {
                'Model Name': self._model_name,
                'Rules Trained': self._ids.rules_trained,
                'DNN Trained': self._ids.dnn_trained,
                'Hidden Units': self._ids.dnn._params['hidden_units'],
                'Activation Function': activation_fn_convert[self._ids.dnn._params['activation_fn']],
                'Optimizer': optimizer_convert[type(self._ids.dnn._params['optimizer'])],
                'Loss Reduction': loss_reduction_convert[self._ids.dnn._params['loss_reduction']]
            }
        else:
            return {
                'Model Name': 'No Model',
                'Rules Trained': False,
                'DNN Trained': False,
                'Hidden Units': '',
                'Activation Function': '',
                'Optimizer': '',
                'Loss Reduction': ''
            }

    @pyqtSlot(str, QJSValue)
    def new_model(self, model_name, parameters):
        self._ids = TwoStageIDS()
        parameters = parameters.toVariant()
        if model_name in self._available_models:
            raise ValueError()
        self._ids.change_ids_parameters('dnn_dir_path', dnnmodels_dir + '/' + model_name)
        self._ids.change_ids_parameters('rules_profile', model_name)
        self._ids.change_dnn_parameters('hidden_units', literal_eval(parameters['Hidden Units']))
        # self._ids.change_dnn_parameters('optimizer', ???)
        self._ids.change_dnn_parameters('activation_fn', activation_fn_convert_reverse[parameters['Activation Function']])
        self._ids.change_dnn_parameters('loss_reduction', loss_reduction_convert_reverse[parameters['Loss Reduction']])
        self._ids.init_ids()

        self._model_name = model_name
        self.get_parameters.emit()
        self._available_models.append(model_name)
        self.get_availableModels.emit()

    @pyqtSlot(str)
    def load_model(self, model_name):
        if model_name not in self._available_models:
            raise ValueError()
        self._ids.change_ids_parameters('dnn_dir_path', dnnmodels_dir + '/' + model_name)
        self._ids.change_ids_parameters('rules_profile', model_name)
        self._ids.init_ids()

        self._model_name = model_name
        self.get_parameters.emit()

    @pyqtSlot(str)
    def delete_model(self, model_name):
        if model_name not in self._available_models:
            raise ValueError()
        if model_name == self._model_name:
            raise RuntimeError()
        params_file = dnnmodels_dir + '/' + model_name + '.params'
        if os.path.exists(params_file):
            os.remove(params_file)
        model_dir = dnnmodels_dir + '/' + model_name
        rules_profile_dir = ruleprofiles_dir + '/' + model_name
        for dir in [model_dir, rules_profile_dir]:
            if os.path.exists(dir):
                shutil.rmtree(dir)

        self._available_models.remove(model_name)
        self.get_availableModels.emit()

    @pyqtSlot(str)
    def train_rules(self, dataset_name):
        canlist = dp.load_canlist(datasets_dir + '/' + dataset_name + '/good_canlist.json')
        self._ids.retrain_rules(canlist)
        self.get_parameters.emit()

    @pyqtSlot(str, int)
    def train_dnn(self, dataset_name, num_steps):
        features, labels = dp.load_feature_lists(datasets_dir + '/' + dataset_name + '/features_labels.json')
        self._ids.train_dnn(dnn_input_function(features, labels, shuffle=True), num_steps)
        self.get_parameters.emit()

    @pyqtSlot()
    def start_simulation(self):
        self._ids.start_simulation()

    # This is distinctly not a slot, because it will be called by the Simulation
    # Manager, which will take this class in its constructor.
    def judge_single_frame(self, can_frame):
        result = self._ids.judge_single_frame(can_frame)
        self.judgement_result.emit(result)

    @pyqtSlot()
    def stop_simulation(self):
        self._ids.stop_simulation()
