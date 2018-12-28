import json
import math
import numpy as np
import tensorflow as tf

from NNIDS.canclass import CANMessage


class MessageClassifier:
    def __init__(self, model_destination_dir,
                 probability_file='data/traffic_analysis_dump/id_occurrences.json', verbose=True):
        """
        Class for training DNNClassifier in TensorFlow

        :param model_destination_dir: Directory to save model to
        """
        print('Setting up DNNClassifier')

        self.probability_file = probability_file
        self.known_messages = self.get_known_messages()
        self.current_entropy = 0

        if verbose is True:
            tf.logging.set_verbosity(tf.logging.INFO)

        self.batch_size = 750
        self.num_steps = 2000

        self.model_dir = model_destination_dir
        self.msg_id_column = tf.feature_column.numeric_column('msg_id', dtype=tf.float32)
        self.occurrences_column = tf.feature_column.numeric_column('occurrences_in_last_s',
                                                                   dtype=tf.float32)
        self.rel_entropy_column = tf.feature_column.numeric_column('relative_entropy',
                                                                   dtype=tf.float32)
        self.delta_entropy = tf.feature_column.numeric_column('delta_entropy', dtype=tf.float32)

        config_obj = tf.estimator.RunConfig().replace(save_checkpoints_steps=50000,
                                                      keep_checkpoint_max=20,
                                                      log_step_count_steps=50000,
                                                      save_summary_steps=2)
        self.classifier \
            = tf.estimator.DNNClassifier(feature_columns=[self.msg_id_column,
                                                          self.occurrences_column,
                                                          self.rel_entropy_column,
                                                          self.delta_entropy],
                                         hidden_units=[10,20,20, 20],
                                         model_dir=self.model_dir,
                                         optimizer=tf.train.ProximalAdagradOptimizer(
                                             learning_rate=0.1,
                                             l1_regularization_strength=0.001,
                                             l2_regularization_strength=3.0
                                         ),
                                         n_classes=2,
                                         weight_column='weights',
                                         config=config_obj)
        print('Finished setting up DNNClassifier')

    def train_classifier(self, features, labels):
        """
        Trains DNN Classifier

        :param features: list of features corresponding to each message in the form
        [[Message ID, Occurrences in last second, Relative Entropy, Change in System Entropy,
        weight]]
        :param labels: list of labels for each message, 1 for malicious and 0 for normal
        :return: None
        :raises ValueError: if the number of messages and the number of labels are not equal
        """
        if len(features) != len(labels):
            raise ValueError('len(msgs) not equal to len(labels): ' + str(len(features))
                             + ' != ' + str(len(labels)))

        msg_ids = []
        occurrences = []
        rel_entropies = []
        delta_entropies = []
        weights = []
        for msg in features:
            msg_ids.append(msg[0])
            occurrences.append(msg[1])
            rel_entropies.append(msg[2])
            delta_entropies.append(msg[3])
            weights.append(msg[4])

        x = {'msg_id': np.array(msg_ids),
             'occurrences_in_last_s': np.array(occurrences),
             'relative_entropy': np.array(rel_entropies),
             'delta_entropy': np.array(delta_entropies),
             'weights': np.array(weights)}

        y = np.array(labels)

        train_input_fn = tf.estimator.inputs.numpy_input_fn(x, y, num_epochs=3,
                                                            batch_size=self.batch_size,
                                                            shuffle=True)
        self.classifier.train(train_input_fn, steps=self.num_steps)

        print('Trained classifier!')

    def test_classifier(self, features, labels):
        """
        Tests DNN Classifier

        :param features: list of features corresponding to each message in the form
        [[Message ID, Occurrences in last second, Relative Entropy, Change in System Entropy]]
        :param labels: list of labels for each message, 1 for malicious and 0 for normal
        :return: None
        :raises ValueError: if the number of messages and the number of labels are not equal
        """
        if len(features) != len(labels):
            raise ValueError('len(msgs) not equal to len(labels): ' + str(len(features))
                             + ' != ' + str(len(labels)))

        msg_ids = []
        occurrences = []
        rel_entropies = []
        delta_entropies = []
        weights = []
        for msg in features:
            msg_ids.append(msg[0])
            occurrences.append(msg[1])
            rel_entropies.append(msg[2])
            delta_entropies.append(msg[3])
            weights.append(msg[4])

        x = {'msg_id': np.array(msg_ids),
             'occurrences_in_last_s': np.array(occurrences),
             'relative_entropy': np.array(rel_entropies),
             'delta_entropy': np.array(delta_entropies),
             'weights': np.array(weights)}

        y = np.array(labels)

        test_input_fn = tf.estimator.inputs.numpy_input_fn(x, y, num_epochs=1,
                                                           batch_size=self.batch_size,
                                                           shuffle=False)

        # Evaluate accuracy.
        accuracy_score = self.classifier.evaluate(input_fn=test_input_fn,
                                                  steps=self.num_steps)["accuracy"]

        print("\nTest Accuracy: {0:f}\n".format(accuracy_score))

    def predict_class(self, features):
        """
        Uses DNN Classifier to predict message class

        :param features: list of features corresponding to each message in the form
        [[Message ID, Occurrences in last second, Relative Entropy, Change in System Entropy]]
        :return: list with class predictions
        """
        msg_ids = []
        occurrences = []
        rel_entropies = []
        delta_entropies = []
        for msg in features:
            msg_ids.append(msg[0])
            occurrences.append(msg[1])
            rel_entropies.append(msg[2])
            delta_entropies.append(msg[3])

        x = {'msg_id': np.array(msg_ids),
             'occurrences_in_last_s': np.array(occurrences),
             'relative_entropy': np.array(rel_entropies),
             'delta_entropy': np.array(delta_entropies)}

        predict_input_fn = tf.estimator.inputs.numpy_input_fn(x, num_epochs=1,
                                                              batch_size=self.batch_size,
                                                              shuffle=False)

        predictions = list(self.classifier.predict(input_fn=predict_input_fn))
        return [p["classes"] for p in predictions]

    def prediction_wrapper(self, can_msg, msg_log_list, msg_occurrences_dict):
        """
        Returns prediction from DNN

        :param can_msg: CANMessage, incoming CAN message
        :param msg_log_list: list of all CAN messages seen, most recent last
        :param msg_occurrences_dict: dict of seen CAN message IDs with occurrences and key 'Total'
        :return: True if message is predicted to be malicious, False otherwise
        """
        [p, q] = self.get_probability_distributions(can_msg.id_float, msg_occurrences_dict)
        new_entropy = self.calculate_entropy(msg_occurrences_dict)

        if len(msg_occurrences_dict) == 1:
            self.current_entropy = new_entropy

        feature = [[can_msg.id_float, self.find_num_occurrences_in_last_second(len(msg_log_list) - 1,
                                                                               can_msg.id_float,
                                                                               can_msg.timestamp,
                                                                               msg_log_list),
                    self.calculate_relative_entropy(q, p), new_entropy - self.current_entropy]]

        self.current_entropy = new_entropy

        prediction = self.predict_class(feature)[0][0]

        if int(prediction) == 1:
            return True
        return False

    def get_known_messages(self):
        """
        Generate dict with known messages from a file

        :return: dict representation of file contents
        """
        known_messages = {}
        with open(self.probability_file, 'r') as infile:
            temp_msgs = json.load(infile)

        for key in temp_msgs:
            known_messages[int(key, 16)] = temp_msgs[key]

        return known_messages

    def calculate_entropy(self, map_of_ids):
        """
        Calculate system entropy

        :param map_of_ids: dict of message IDs and their respective number of occurrences,
        as well as the total number of messages that have passed through the system
        :return: the calculated system entropy
        """
        system_entropy = 0
        for msg_id in map_of_ids:
            probability = map_of_ids[msg_id] / map_of_ids['Total']
            system_entropy = system_entropy + probability * math.log(1.0 / probability)

        return system_entropy

    def calculate_relative_entropy(self, normal, measured):
        """
        Calculate the relative entropy of a particular message ID

        :param normal: the normal probability
        :param measured: the measured probability
        :return: the relative entropy
        """
        if normal == 0:
            return 100
        return measured * math.log(measured / normal)

    def get_probability_distributions(self, msg_id, empirical):
        """
        Return the probability distribution of a message ID

        :param msg_id: the message ID to search for
        :param empirical: measured data
        :return: list of [probability in known messages, measured probability]
        """
        if msg_id in self.known_messages:
            q = self.known_messages[msg_id]['Probability']
        else:
            q = 0
        p = empirical[msg_id] / empirical['Total']

        return [p, q]

    def find_num_occurrences_in_last_second(self, index, msg_id, timestamp, messages):
        """
        Return the number of occurrences of this message ID in the past second.
        Assume timestamps in milliseconds.

        :param index: index of this message in messages
        :param msg_id: the message ID to search for
        :param timestamp: the timestamp of this message
        :param messages: list of CANMessage objects previously seen on the bus,
            in order from earliest to most recent
        :return: the number of occurrences of this message ID in the past second
        """
        count = 0
        for j in range(index, 0, -1):
            if timestamp - messages[j].timestamp <= 1000:
                if messages[j].id_float == msg_id:
                    count = count + 1
            else:
                break
        return count
