from ids.dnn_ids import DNNBasedIDS
from ids.rules_ids import RulesIDS
import ids.preprocessor as dp
from numpy import log
import os.path

class TwoStageIDS:  # pylint: disable=too-many-instance-attributes
    """A class that uses both the set of rules (Rules Based IDS) and a trained deep neural network (DNN Based IDS) for classification."""
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
        """Initialize the Rules Based IDS, DNN Based IDS, and other components
        of the Two Stage IDS based on the parameters that were specified with
        change_ids_parameters. If a parameter was not specified, the respective
        component of the Two Stage IDS will not be initialized.

        Returns nothing. Must be called before an judging of packets or
        simulations are started.
        """
        if self.params['dnn_dir_path']:
            # If the DNN model trying to be loaded has
            # been created, then a .params file will exist.
            if os.path.exists(self.params['dnn_dir_path'] + '.params'):
                print('Loading existing DNN model')
                self.dnn.load_model(self.params['dnn_dir_path'])
            else:
                print('Creating new DNN model')
                self.dnn.new_model(self.params['dnn_dir_path'])
            # If the DNN model trying to be loaded has
            # been trained, then the checkpoint folder will exist.
            if os.path.exists(self.params['dnn_dir_path']):
                self.dnn_trained = True
            else:
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
        """Change the parameters of the Two Stage IDS.

        Arguments:
        key -- Name of the parameter to change. There are 4 valid parameters:
            dnn_dir_path -- The DNN model directory to be used. No default
            value.
            rules_profile -- The name of the Rules Based IDS profile ID to use. No default value.
            idprobs_path -- The path to the ID probabilities file of the vehicle
            this IDS will be processing. No default value.
        value -- What to change the value of the parameter to.

        Raises:
        ValueError -- A key that is not one of the 3 valid parameters is
        specified.
        """
        if key not in self.params:
            raise ValueError(f'{key} is not a valid parameter that can be changed. Valid parameters: {list(self.params.keys())}')
        else:
            self.params[key] = value

    def change_dnn_parameters(self, key, value):
        """Changes the specific parameters of the DNN Based IDS inside the Two Stage IDS. See documentation for DNNBasedIDS.change_param() for more information.
        """
        self.dnn.change_param(key, value)

    def retrain_rules(self, canlist):
        """Take a list of CAN frames and retrain the Rules Based IDS based on the list provided.

        Arguments:
        canlist -- List of CAN frames to be used to retrain the Rules Based IDS.

        Returns nothing, but marks the Rules Based IDS as trained.
        """
        self.rules.prepare(canlist, self.params['rules_profile'])
        self.rules_trained = True

    def train_dnn(self, input_function, num_steps):
        """Train the DNN based part of the Two Stage IDS with data from the
        input function for a certain number of steps.

        Arguments:
        input_function -- The input function for the dataset the DNN should be
        trained on.
        num_steps -- The number of steps to take for training the DNN.

        Returns nothing, but marks the DNN Based IDS as trained.
        """
        if not self.dnn._dnn:
            raise RuntimeError('No DNN has been initialized!')
        self.dnn.train(input_function, num_steps)
        self.dnn_trained = True

    def _judge_dataset(self, canlist, input_function):
        """Helper function for judge_dataset that creates the actual generator returned. Should never be used normally.
        """
        rules_results = self.rules.test_series(canlist)
        dnn_results = self.dnn.predict(input_function)
        for rule_result, dnn_result in zip(rules_results, dnn_results):
            if not rule_result[0]:
                yield rule_result
            else:
                yield dnn_result

    def judge_dataset(self, canlist, input_function):
        """Take a list of CAN frames as well as an input function, and run the frames through the Two Stage IDS and get the classifications of each frame. The Two Stage IDS must not be in a simulation in order for this function to work.

        Arguments:
        canlist -- The list of CAN frames to run against the Two Stage IDS.
        input_function -- An input function containing the processed frames.
        One should use the dnn_input_function() from the dnn_ids module, and
        pass it a list of processed frames from
        preprocessor.generate_feature_lists() and labels from
        preprocessor.inject_malicious_packets().

        Raises:
        RuntimeError -- A simulation has been started with the function
        start_simulation, or the Rules Based IDS or DNN Based IDS have not been trained.

        Returns a generator yielding one of three types of tuples:
        (True, str): The frame is malicious, and the string is the name of the
        rule that rejected the frame.
        (True, float): The frame is malicious, and the float value is the
        confidence of the DNN in its prediction.
        (False, float): The frame is not malicious, and the float value is the
        confidence of the DNN in its prediction.
        """
        if self.in_simulation:
            raise RuntimeError('The TwoStageIDS must not be in a simulation in order to judge a dataset.')
        elif not self.dnn_trained:
            raise RuntimeError('The DNN must be trained before judging a dataset.')
        elif not self.rules_trained:
            raise RuntimeError('The Rules Based IDS must be prepared before judging a dataset.')
        else:
            return self._judge_dataset(canlist, input_function)


    def start_simulation(self):
        """Start a simulation of the Two Stage IDS, which allows the ability to feed the Two Stage IDS single CAN frames at a time in order to be classified, instead of having to preprocess the frames. Both the Rules Based IDS and DNN Based IDS must be trained before this can be started.

        Raises:
        RuntimeError -- The Two Stage IDS is already in a simulation, or the
        Rules Based IDS or DNN Based IDS are not trained.
        """
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
        """Stop a simulation of the Two Stage IDS.

        Raises:
        RuntimeError -- The Two Stage IDS is not in a simulation.
        """
        if not self.in_simulation:
            raise RuntimeError('The TwoStageIDS is not currently in a simulation.')
        self.in_simulation = False

    def judge_single_frame(self, frame):
        """Take a single CAN frame, and run the frames through the Two Stage
        IDS and get the classification of the frame. The Two Stage IDS must be
        in a simulation in order for this function to work.

        Arguments:
        canlist -- The list of CAN frames to run against the Two Stage IDS.
        input_function -- An input function containing the processed frames.
        One should use the dnn_input_function() from the dnn_ids module, and
        pass it a list of processed frames from
        preprocessor.generate_feature_lists() and labels from
        preprocessor.inject_malicious_packets().

        Raises:
        RuntimeError -- A simulation has not been started with the function
        start_simulation.

        Returns a tuple that is one of the following types below:
        (True, str): The frame is malicious, and the string is the name of the
        rule that rejected the frame.
        (True, float): The frame is malicious, and the float value is the
        confidence of the DNN in its prediction.
        (False, float): The frame is not malicious, and the float value is the
        confidence of the DNN in its prediction.
        """
        if not self.in_simulation:
            raise RuntimeError('The TwoStageIDS is not currently in a simulation.')
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
