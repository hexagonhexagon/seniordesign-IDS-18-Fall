import tensorflow as tf
import numpy as np
import os.path
import pickle

feature_cols = [
    tf.feature_column.numeric_column(
        'id', dtype=tf.uint16),  # Should this be a categorical column?
    tf.feature_column.numeric_column(
        'occurrences_in_last_sec', dtype=tf.uint16),
    tf.feature_column.numeric_column('relative_entropy'),
    tf.feature_column.numeric_column('system_entropy_change')
]


class DNNBasedIDS:
    """A class that uses a neural network to classify packets.

    Properties:
    _params: Stores the parameters of the DNN based IDS. There are 4 parameters:
        hidden_units -- List specifying the number of hidden layers and number
        of neurons in each layer. Default [10, 20, 20, 20].
        optimizer -- The optimizer to use in helping the neural network learn.
        Default is the ProximalAdagradOptimizer with learning rate 0.1, L1
        regularization strength 0.001, and L2 regularization strength 3.0.
        activation_fn -- The activation function to use for each neuron. Default is relu.
        loss_reduction -- The loss reduction algorithm to use. Default is SUM.

    Functions:
    __init__ -- Initialize the parameters of the DNN based IDS to their defaults.
    change_param -- Change the parameters of the DNN based IDS.
    new_model -- Create a new model with the directory specified.
    load_model -- Load the model from the directory specified.
    train -- Train the DNN based IDS with data from the input function for a certain number of steps.
    predict_frame -- Determine if a pre-processed frame is malicious or not.
    predict -- Take an input function for a data set and return whether the frames are malicious or not.
    """
    def __init__(self):
        """Initialize the parameters of the DNN based IDS to their defaults."""
        self._params = {
            'hidden_units': [10, 20, 20, 20],
            'optimizer':
            tf.train.ProximalAdagradOptimizer(
                learning_rate=0.1,
                l1_regularization_strength=0.001,
                l2_regularization_strength=3.0),
            'activation_fn':
            tf.nn.relu,
            'loss_reduction':
            tf.losses.Reduction.SUM  # Never used?
        }
        self._dnn = None

    def change_param(self, key, value):
        """Change the parameters of the DNN based IDS.

        Arguments:
        key -- Name of the parameter to change. There are 4 valid parameters:
            hidden_units -- List specifying the number of hidden layers and
            number of neurons in each layer. Default [10, 20, 20, 20].
            optimizer -- The optimizer to use in helping the neural network
            learn. Default is the ProximalAdagradOptimizer with learning rate
            0.1, L1 regularization strength 0.001, and L2 regularization
            strength 3.0.
            activation_fn -- The activation function to use for each neuron.
            Default is relu.
            loss_reduction -- The loss reduction algorithm to use. Default is
            SUM.
        value -- What to change the value of the parameter to.

        Raises:
        ValueError -- A key that is not one of the 4 valid parameters is
        specified.
        RuntimeError -- A DNN model has already been loaded. The parameters of a
        DNN cannot be changed after it has been created.
        """
        if self._dnn:
            raise RuntimeError(
                'Cannot change the parameters of an already initialized DNN!')
        if key not in self._params:
            raise ValueError(
                '{} is not a valid parameter that can be changed. Valid keys: {}'
                .format(key, self._params.keys()))
        self._params[key] = value

    def new_model(self, model_dir):
        """Create a new model with the directory specified.

        Arguments:
        model_dir -- The directory to which this model should be saved.

        Raises:
        FileExistsError -- A model with the same name already exists, so a new
        model cannot be created.
        """
        if os.path.exists(model_dir):
            raise FileExistsError('A model with that name already exists!')
        with open(model_dir + '.params', 'w+b') as file:
            pickle.dump(self._params, file)
        self._dnn = tf.estimator.DNNClassifier(
            feature_columns=feature_cols,
            hidden_units=self._params['hidden_units'],
            model_dir=model_dir,
            n_classes=2,
            weight_column=None,  # Do we want weight column?
            label_vocabulary=None,
            optimizer=self._params['optimizer'],
            activation_fn=self._params['activation_fn'],
        )

    def load_model(self, model_dir):
        """Load the model from the directory specified.

        Arguments:
        model_dir -- The directory the model should be loaded from.

        Raises:
        FileNotFoundError -- There is no model with the name specified in the
        directory specified.
        """
        if not os.path.exists(model_dir + '.params'):
            raise FileNotFoundError(
                'The model {} does not exist!'.format(model_dir))
        with open(model_dir + '.params', 'rb') as file:
            self._params = pickle.load(file)
        self._dnn = tf.estimator.DNNClassifier(
            feature_columns=feature_cols,
            hidden_units=self._params['hidden_units'],
            model_dir=model_dir,
            n_classes=2,
            weight_column=None,  # Do we want weight column?
            label_vocabulary=None,
            optimizer=self._params['optimizer'],
            activation_fn=self._params['activation_fn'],
            loss_reduction=self._params['loss_reduction']
        )

    def train(self, input_function, num_steps):
        """Train the DNN based IDS with data from the input function for a certain number of steps.

        Arguments:
        input_function -- The input function for the dataset the DNN based IDS
        should be trained on.
        num_steps -- The number of steps to take for training the DNN based IDS.
        """
        self._dnn.train(input_function, steps=num_steps)

    def predict_frame(self, processed_frame):
        """Determine if a pre-processed frame is malicious or not.

        Arguments:
        processed_frame -- A pre-processed frame that has the ID, number of
        occurrences of this frame in the last second, change in system entropy,
        and relative entropy.

        Returns a pair (is_malicious, prob_malicious). is_malicious is a boolean
        stating if the frame is malicious, and prob_malicious is a float
        describing the probability the frame is malicious.
        """
        features = {k: np.array(v) for k, v in processed_frame.items()}
        input_function = tf.estimator.inputs.numpy_input_fn(
            features, y=None, batch_size=1)
        predictions = self._dnn.predict(input_function)
        prediction = list(predictions)[0]
        is_malicious = bool(prediction['class_ids'][0])
        prob_malicious = prediction['probabilities'][1]
        return is_malicious, prob_malicious

    def predict(self, input_function):
        """Take an input function for a data set and return whether the frames are malicious or not.

        Arguments:
        input_function -- The input function for the dataset the DNN based IDS
        should predict results for.

        Returns a generator that yields pairs (is_malicious, prob_malicious)
        when iterated through. is_malicious is a boolean
        stating if the frame is malicious, and prob_malicious is a float
        describing the probability the frame is malicious.
        """
        predictions = self._dnn.predict(input_function)
        return map(lambda x: (bool(x['class_ids'][0]), x['probabilities'][1]),
                   predictions)
