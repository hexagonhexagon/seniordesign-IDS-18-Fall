import tensorflow as tf
import numpy as np

class DNNBasedIDS:
    def __init__(self, model_dir):
        self.params = {
            'hidden_units': [10, 20, 20, 20],
            'model_dir': model_dir,
            'optimizer': tf.train.ProximalAdagradOptimizer(
                learning_rate=0.1,
                l1_regularization_strength=0.001,
                l2_regularization_strength=3.0
            ),
            'activation_fn': tf.nn.relu,
            'loss_reduction': tf.losses.Reduction.SUM # Never used?
        }
        self._dnn = None # We initialize this in another function.

    def change_param(self, key, value):
        if key not in self.params:
            raise ValueError('{} is not a valid parameter that can be changed.'.format(key))
        self.params[key] = value

    def initialize(self):
        self._dnn = tf.estimator.DNNClassifier(
            feature_columns=[
                tf.feature_column.numeric_column('id', dtype=tf.uint16),
                tf.feature_column.numeric_column('occurrences_in_last_sec', dtype=tf.uint16),
                tf.feature_column.numeric_column('relative_entropy'),
                tf.feature_column.numeric_column('system_entropy_change')
            ],
            hidden_units=self.params['hidden_units'],
            model_dir=self.params['model_dir'],
            n_classes=2,
            weight_column='weights', # Do we want weight column?
            label_vocabulary=None, # Do we want label vocabulary?
            optimizer=self.params['optimizer'],
            activation_fn=self.params['activation_fn'],
        )

    def train(self, input_function, num_steps):
        self._dnn.train(input_function, steps=num_steps)

    def predict_frame(self, processed_frame):
        features = {k: np.array(v) for k, v in processed_frame.items()}
        input_function = tf.estimator.inputs.numpy_input_fn(features, y=None, batch_size=1)
        predictions = self._dnn.predict(input_function)
        prediction = list(predictions)[0]
        is_malicious = bool(prediction['class_ids'][0])
        prob_malicious = prediction['probabilities'][1]
        return is_malicious, prob_malicious

    def predict(self, input_function):
        predictions = self._dnn.predict(input_function)
        return map(lambda x: (bool(x['class_ids'][0]), x['probabilities'][1]), predictions)