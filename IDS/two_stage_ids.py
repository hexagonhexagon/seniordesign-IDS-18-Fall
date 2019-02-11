from IDS.dnn_ids import DNNBasedIDS
from IDS.rules_ids import RulesIDS
import IDS.preprocessor as dp
from numpy import log
import os.path

class TwoStageIDS:  # pylint: disable=too-many-instance-attributes
    """Intrusion Detection System using two stages for classification.

    """
    def __init__(self):
        self.dnn_trained = False
        self.rules_trained = False
        self.in_simulation = False

        self.dnn = DNNBasedIDS()
        self.rules = RulesIDS()
        self.idprobs = {}

        self.params = {
            'dnn_dir_path': None,
            'rules_profile': None,
            'idprobs_path': None
        }
        # Simulation variables start here.
        self.id_freq = dp.ID_Past()
        self.id_entr = dp.ID_Entropy()

    def init_ids(self):
        if self.params['dnn_dir_path']:
            # If the DNN model trying to be loaded has
            # been trained, then a .params file will exist.
            if os.path.exists(self.params['dnn_dir_path'] + '.params'):
                print('Loading existing DNN model')
                self.dnn.load_model(self.params['dnn_dir_path'])
                self.dnn_trained = True
            else:
                print('Creating new DNN model')
                self.dnn.new_model(self.params['dnn_dir_path'])
                self.dnn_trained = False
        if self.params['rules_profile']:
            self.rules.profile_id = self.params['rules_profile']
            try:
                self.rules.prepare() # If the profile ID provided hasn't been
                                     # prepared, an error will be thrown
                print('Loading existing Rules IDS profile')
                self.rules_trained = True
            except FileNotFoundError:
                print('Creating new Rules IDS profile')
                self.rules_trained = False
        if self.params['idprobs_path']:
            self.idprobs = dp.load_id_probs(self.params['idprobs_path'])

    def change_ids_parameters(self, key, value):
        if key not in self.params:
            raise ValueError(f'{key} is not a valid parameter that can be changed. Valid parameters: {list(self.params.keys())}')
        else:
            self.params[key] = value

    def change_dnn_parameters(self, key, value):
        self.dnn.change_param(key, value)

    def retrain_rules(self, canlist):
        self.rules.prepare(canlist, self.params['rules_profile'])
        self.rules_trained = True

    def retrain_dnn(self, input_function, num_steps):
        if not self.dnn._dnn:
            raise RuntimeError('No DNN has been initialized!')
        self.dnn.train(input_function, num_steps)
        self.dnn_trained = True

    def judge_dataset(self, canlist, input_function):
        if self.in_simulation:
            raise RuntimeError('The TwoStageIDS must not be in a simulation in order to judge a dataset.')
        rules_results = self.rules.test_series(canlist)
        dnn_results = self.dnn.predict(input_function)
        for rule_result, dnn_result in zip(rules_results, dnn_results):
            if not rule_result[0]:
                yield rule_result
            else:
                yield dnn_result

    def start_simulation(self):
        if self.in_simulation:
            raise RuntimeError('The TwoStageIDS has already begun a simulation!')
        if not self.dnn_trained:
            raise RuntimeError('The DNN must be trained before a simulation can be started!')
        if not self.rules_trained:
            raise RuntimeError('The Rules Based IDS must be prepared before a simulation can be started!')
        self.in_simulation = True
        self.id_freq = dp.ID_Past()
        self.id_entr = dp.ID_Entropy()

    def stop_simulation(self):
        if not self.in_simulation:
            raise RuntimeError('The TwoStageIDS is not currently in a simulation.')
        self.in_simulation = False

    def judge_single_frame(self, frame):
        is_malicious = self.rules.test(frame)
        if is_malicious[0]: # is_malicious is a pair (is_malicious, rule_name)
            return is_malicious
        else:  # Passed RuleBasedIDS, test against DNNBasedIDS.
            processed_frame = {'id': id}
            processed_frame['occurrences_in_last_sec'] = next(
                self.id_freq.feed([frame]))

            e_relative, e_system = next(
                self.id_entr.feed([frame], self.idprobs))
            processed_frame['relative_entropy'] = e_relative
            processed_frame['system_entropy_change'] = e_system

            return self.dnn.predict_frame(processed_frame)
