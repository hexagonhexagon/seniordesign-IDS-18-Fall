from IDS.dnn_ids import DNNBasedIDS
from IDS.rules_ids import RulesIDS
import IDS.preprocessor as dp
from numpy import log

class TwoStageIDS:
    def __init__(self):
        self.dnn_trained = False
        self.rules_trained = False
        self.in_simulation = False

        self.dnn = DNNBasedIDS()
        self.rules = RulesIDS()
        self.idprobs = {}

        self.params = {
            'dnn_dir_path': None,
            'rules_dir_path': None,
            'idprobs_path': None
        }
        # Simulation variables start here.
        self.frames_last_sec = []
        self.idcounts = {}
        self.total_frames = 0
        self.system_entropy = 0

    def load_ids(self):
        if self.params['dnn_dir_path']:
            self.dnn.load_model(self.params['dnn_dir_path'])
            self.dnn_trained = True
        if self.params['rules_dir_path']:
            self.rules.prepare(set_profile_id=self.params['rules_dir_path'])
            self.rules_trained = True
        if self.params['idprobs_path']:
            self.idprobs = dp.load_id_probs(self.params['idprobs_path'])

    def change_ids_parameters(self, key, value):
        if key not in self.params:
            raise ValueError(f'{key} is not a valid parameter that can be changed. Valid parameters: {list(self.params.keys())}')
        else:
            self.params[key] = value

    def retrain_rules(self, canlist):
        self.rules.prepare(canlist)
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
        self.frames_last_sec = []
        self.idcounts = {}
        self.total_frames = 0
        self.system_entropy = 0
        self.in_simulation = True

    def stop_simulation(self):
        if not self.in_simulation:
            raise RuntimeError('The TwoStageIDS is not currently in a simulation.')
        self.in_simulation = False

    def judge_single_frame(self, frame):
        is_malicious = self.rules.test(frame)
        if is_malicious[0]: # is_malicious is a pair (is_malicious, rule_name)
            return is_malicious
        else: # Passed RuleBasedIDS, test against DNNBasedIDS.
            self.frames_last_sec.append(frame)
            # Remove frames from frames_last_sec older than 10000 0.1ms
            # increments from this frame.
            self.frames_last_sec = list(filter(
                lambda x: frame['timestamp'] - x['timestamp'] < 10000,
                self.frames_last_sec
            ))
            id = frame['id']
            self.idcounts.setdefault(id, 0)
            self.idcounts[id] += 1
            self.total_frames += 1

            processed_frame = {'id': id}

            occurrences_in_last_sec = 0
            for old_frame in self.frames_last_sec:
                if old_frame['id'] == frame['id']:
                    occurrences_in_last_sec += 1
            processed_frame['occurrences_in_last_sec'] = occurrences_in_last_sec

            p = self.idcounts[frame['id']] / self.total_frames
            q = self.idprobs.get(frame['id'], 0)
            if q == 0:
                processed_frame['relative_entropy'] = 100
            else:
                processed_frame['relative_entropy'] = p * log(p / q)

            old_system_entropy = self.system_entropy
            self.system_entropy = 0
            for idcount in self.idcounts.values():
                p = idcount / self.total_frames
                self.system_entropy -= p * log(p)
            processed_frame['system_entropy_change'] = (self.system_entropy
                - old_system_entropy)

            return self.dnn.predict_frame(processed_frame)
