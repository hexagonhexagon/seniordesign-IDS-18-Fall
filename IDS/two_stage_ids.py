from dnn_ids import DNNBasedIDS
import rules_ids as RuleBasedIDS
from numpy import log

class TwoStageIDS:
    def __init__(self):
        self.has_been_trained = False
        self.in_simulation = False
        self.params = {} # Should be initialized like the DNNBasedIDS.
        self.dnn = DNNBasedIDS()
        self.idprobs = {} # This needs to be loaded from a file properly.
                          # Possibly integrate into params.
        # Simulation variables start here.
        self.frames_last_sec = []
        self.idcounts = {}
        self.total_frames = 0
        self.system_entropy = 0
        # Do more initialization here.

    def change_ids_parameters(self, key, value):
        pass

    def retrain_on_dataset(self, input_function):
        pass

    def judge_dataset(self, input_function):
        pass

    def start_simulation(self):
        if self.in_simulation:
            raise RuntimeError('The TwoStageIDS has already begun a simulation!')
        if not self.has_been_trained:
            raise RuntimeError('The DNN must be trained before a simulation can be started!')
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
        is_malicious = RuleBasedIDS.test(frame)
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
