from dnn_ids import DNNBasedIDS
# Import RuleBasedIDS.

class TwoStageIDS:
    def __init__(self):
        self.has_been_trained = False
        self.in_simulation = False
        self.params = {} # Should be initialized like the DNNBasedIDS.
        # Do more initialization here.

    def change_ids_parameters(self, key, value):
        pass

    def retrain_on_dataset(self, input_function):
        pass

    def judge_dataset(self, input_function):
        pass

    def start_simulation(self):
        pass

    def stop_simulation(self):
        pass

    def judge_single_frame(self, frame):
        pass