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
    def __init__(self):
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
        if self._dnn:
            raise RuntimeError(
                'Cannot change the parameters of an already initialized DNN!')
        if key not in self._params:
            raise ValueError(
                '{} is not a valid parameter that can be changed. Valid keys: {}'
                .format(key, self._params.keys()))
        self._params[key] = value

    def new_model(self, model_dir):
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
        )

    def train(self, input_function, num_steps):
        self._dnn.train(input_function, steps=num_steps)

    def predict_frame(self, processed_frame):
        features = {k: np.array(v) for k, v in processed_frame.items()}
        input_function = tf.estimator.inputs.numpy_input_fn(
            features, y=None, batch_size=1)
        predictions = self._dnn.predict(input_function)
        prediction = list(predictions)[0]
        is_malicious = bool(prediction['class_ids'][0])
        prob_malicious = prediction['probabilities'][1]
        return is_malicious, prob_malicious

    def predict(self, input_function):
        predictions = self._dnn.predict(input_function)
        return map(lambda x: (bool(x['class_ids'][0]), x['probabilities'][1]),
                   predictions)
