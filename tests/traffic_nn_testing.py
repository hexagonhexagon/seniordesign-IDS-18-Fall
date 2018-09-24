"""
Script for testing the neutral network on .traffic files, note that is it trained on .traffic data and
uses the TensorFlow model in traffic_ids
"""

from collections import deque
import math
import numpy as np
import os
import sys
import time

from NNIDS.analyzers.accuracy import AccuracyAnalyzer
from NNIDS.analyzers.operation import OperationAnalyzer
from NNIDS.canclass import CANMessage
from NNIDS.classifier_impl import MessageClassifier
from NNIDS.parsers import traffic


max_log_interval = 120000

traffic_datasets = {
    'probability': os.getcwd() + '/data/traffic_analysis_dump/id_occurrences.json',
    'train': os.getcwd() + '/data/traffic/local_Aug_31.traffic',
    'test': os.getcwd() + '/data/traffic/office_local_Aug_31.traffic',
    'model_dir': os.getcwd() + '/traffic_ids'
}

asia_datasets = {
    'probability': os.getcwd() + '/data/traffic_analysis_dump/id_occurrences_asia.json',
    'train': os.getcwd() + '/data/traffic/asia_train.traffic',
    'test': os.getcwd() + '/data/traffic/asia_test.traffic',
    'model_dir': os.getcwd() + '/traffic_ids_asia'
}

datasets = {'asia': asia_datasets, 'traffic': traffic_datasets}


def main(classifier, traffic_file, train, verbose=True, print_test=False, live_classification=False,
         num_to_read=None,  factor_to_read=None, skip_attacks=False):
    """
    Interface with DNNClassifier wrapped in classifier

    :param classifier: MessageClassifier instance
    :param traffic_file: name of .traffic file to load data from
    :param num_to_read: if not None, indicates the number of messages to read from rec_1
    :param factor_to_read: if not None, indicates the percentage of messages to read from rec_1
        Has no effect if num_to_read is not None
    :param verbose: if True, has verbose output
    :param train: if True, trains DNNClassifier instance. If false, tests DNNClassifier instance.
        If train is True, the following arguments have no effect.
    :param print_test:
        if False, tests on the entirety of rec_1, making predictions at the end after all data
            is loaded
        if True, prints attacks and classification result for every message seen.
        Has no effect if live_classification is False.
    :param live_classification: Runs classifier for each message seen as opposed to waiting
        until the end. Needed to enable operation analysis.
    :param skip_attacks: if True, does not generate attacks.
    :return: None
    """

    if train is True:
        print_test = False
        live_classification = False
        # num_to_read = None
        # factor_to_read = None
        skip_attacks = False

    op_analyzer = OperationAnalyzer()

    can_msgs = traffic.traffic_parser(traffic_file)

    features = []
    labels = []
    seen_messages = {'Total': 0}
    previous_entropy = 0
    current_entropy = 0

    msgs_parsed = deque()
    msg_types = []
    if num_to_read is None:
        if factor_to_read is not None:
            num_to_read = int(len(can_msgs) * factor_to_read)
        else:
            num_to_read = len(can_msgs)
    divisor = int(math.log10(num_to_read))
    if divisor > 2:
        divisor -= 2
    else:
        divisor = 2

    for i in range(0, num_to_read):
        if verbose is True:
            if (i - 1) % (10 ** divisor) == 0:
                print('Processed ' + str(i) + ' of ' + str(num_to_read))

        msgs_parsed.append(can_msgs[i])

        seen_messages['Total'] = seen_messages['Total'] + 1
        if can_msgs[i].id_float not in seen_messages:
            seen_messages[can_msgs[i].id_float] = 0
        seen_messages[can_msgs[i].id_float] = seen_messages[can_msgs[i].id_float] + 1

        [p, q] = classifier.get_probability_distributions(can_msgs[i].id_float, seen_messages)

        current_entropy = classifier.calculate_entropy(seen_messages)

        features.append([can_msgs[i].id_float,
                         classifier.find_num_occurrences_in_last_second(len(msgs_parsed) - 1,
                                                                        can_msgs[i].id_float,
                                                                        can_msgs[i].timestamp,
                                                                        msgs_parsed),
                         classifier.calculate_relative_entropy(q, p),
                         current_entropy - previous_entropy, 1])

        labels.append(0)
        previous_entropy = current_entropy
        msg_types.append('Valid')
        if live_classification is True:
            start = time.perf_counter()
            prediction = classifier.prediction_wrapper(msgs_parsed[len(msgs_parsed) - 1],
                                                       msgs_parsed, seen_messages)
            end = time.perf_counter()
            op_analyzer.add_runtime(start, end, 'Valid')

            if prediction is False:
                output_str = 'Valid message is ALLOWED'
            else:
                output_str = 'Valid message is CAUGHT'

            if print_test is True:
                print(output_str)

        if msgs_parsed[len(msgs_parsed) - 1].timestamp - msgs_parsed[0].timestamp \
                >= max_log_interval:
            seen_messages[msgs_parsed[0].id_float] -= 1
            if seen_messages[msgs_parsed[0].id_float] == 0:
                del seen_messages[msgs_parsed[0].id_float]
            seen_messages['Total'] -= 1
            msgs_parsed.popleft()

        if skip_attacks is True:
            continue

        attack_previous_entropy = previous_entropy
        attack_seen_messages = dict(seen_messages)
        attack_msgs_parsed = deque(msgs_parsed)

        rand_num = np.random.randint(0, 25)
        if i < len(can_msgs) - 1 and rand_num == 0:  # 4% chance of inserting random message ID
            rand_id = "{0:#0{1}X}".format(np.random.randint(0, 4096), 5)[2:]
            new_time_stamp = (can_msgs[i].timestamp + can_msgs[i + 1].timestamp) / 2

            new_msg = CANMessage(new_time_stamp, rand_id, 0)
            attack_msgs_parsed.append(new_msg)

            attack_seen_messages['Total'] = attack_seen_messages['Total'] + 1
            if new_msg.id_float not in attack_seen_messages:
                attack_seen_messages[new_msg.id_float] = 0
            attack_seen_messages[new_msg.id_float] = attack_seen_messages[new_msg.id_float] + 1

            [p, q] = classifier.get_probability_distributions(new_msg.id_float,
                                                              attack_seen_messages)
            current_entropy = classifier.calculate_entropy(attack_seen_messages)
            features.append([new_msg.id_float,
                             classifier.find_num_occurrences_in_last_second(len(attack_msgs_parsed) - 1,
                                                                            new_msg.id_float,
                                                                            new_time_stamp,
                                                                            attack_msgs_parsed),
                             classifier.calculate_relative_entropy(q, p),
                             current_entropy - attack_previous_entropy,
                             20])
            labels.append(1)

            msg_types.append('Random injection')

            if live_classification is True:
                start = time.perf_counter()
                prediction = classifier.prediction_wrapper(attack_msgs_parsed[len(attack_msgs_parsed) - 1],
                                                           attack_msgs_parsed,
                                                           attack_seen_messages)
                end = time.perf_counter()
                op_analyzer.add_runtime(start, end, 'Random injection')

                if prediction is False:
                    output_str = 'Malicious message is ALLOWED'
                else:
                    output_str = 'Malicious message is CAUGHT'
                if print_test is True:
                    print(output_str)

            if attack_msgs_parsed[len(attack_msgs_parsed) - 1].timestamp \
                    - attack_msgs_parsed[0].timestamp \
                    >= max_log_interval:
                attack_seen_messages[attack_msgs_parsed[0].id_float] -= 1
                if attack_seen_messages[attack_msgs_parsed[0].id_float] == 0:
                    del attack_seen_messages[attack_msgs_parsed[0].id_float]
                attack_seen_messages['Total'] -= 1
                attack_msgs_parsed.popleft()
        elif i < len(can_msgs) - 1 and rand_num == 1:  # 4% chance of inserting 10 messages with
            # known id
            rand_idx = np.random.randint(0, 13)
            count = 0
            for known_id in sorted(classifier.known_messages.keys()):
                if count == rand_idx:
                    rand_id = known_id
                    break
                count += 1
            time_stamp_step = (can_msgs[i + 1].timestamp - can_msgs[i].timestamp) / 11

            for j in range(1, 11):
                new_time_stamp = can_msgs[i].timestamp + time_stamp_step * i
                new_msg = CANMessage(new_time_stamp, rand_id, 0)
                attack_msgs_parsed.append(new_msg)

                attack_seen_messages['Total'] = attack_seen_messages['Total'] + 1
                if new_msg.id_float not in attack_seen_messages:
                    attack_seen_messages[new_msg.id_float] = 0
                attack_seen_messages[new_msg.id_float] = attack_seen_messages[
                                                             new_msg.id_float] + 1

                [p, q] = classifier.get_probability_distributions(new_msg.id_float,
                                                                  attack_seen_messages)
                current_entropy = classifier.calculate_entropy(attack_seen_messages)
                features.append([new_msg.id_float,
                                 classifier.find_num_occurrences_in_last_second(
                                     len(attack_msgs_parsed) - 1,
                                     new_msg.id_float,
                                     new_time_stamp, attack_msgs_parsed),
                                 classifier.calculate_relative_entropy(q, p),
                                 current_entropy - attack_previous_entropy,
                                 20])
                labels.append(1)

                attack_previous_entropy = current_entropy

                msg_types.append('Spoofing')

                if live_classification is True:
                    start = time.perf_counter()
                    prediction = classifier.prediction_wrapper(
                        attack_msgs_parsed[len(attack_msgs_parsed) - 1],
                        attack_msgs_parsed,
                        attack_seen_messages)
                    end = time.perf_counter()
                    op_analyzer.add_runtime(start, end, 'Spoofing')

                    if prediction is False:
                        output_str = 'Malicious message is ALLOWED'
                    else:
                        output_str = 'Malicious message is CAUGHT'
                    if print_test is True:
                        print(output_str)

                if attack_msgs_parsed[len(attack_msgs_parsed) - 1].timestamp \
                        - attack_msgs_parsed[0].timestamp \
                        >= max_log_interval:
                    attack_seen_messages[attack_msgs_parsed[0].id_float] -= 1
                    if attack_seen_messages[attack_msgs_parsed[0].id_float] == 0:
                        del attack_seen_messages[attack_msgs_parsed[0].id_float]
                    attack_seen_messages['Total'] -= 1
                    attack_msgs_parsed.popleft()

        elif i < len(can_msgs) - 1 and rand_num == 2:  # 4% chance ddos with 10 messages
            rand_id = '000'
            time_stamp_step = (can_msgs[i + 1].timestamp - can_msgs[i].timestamp) / 21

            for j in range(1, 21):
                new_time_stamp = can_msgs[i].timestamp + time_stamp_step * i
                new_msg = CANMessage(new_time_stamp, rand_id, 0)
                attack_msgs_parsed.append(new_msg)

                attack_seen_messages['Total'] = attack_seen_messages['Total'] + 1

                if new_msg.id_float not in attack_seen_messages:
                    attack_seen_messages[new_msg.id_float] = 0

                attack_seen_messages[new_msg.id_float] = attack_seen_messages[new_msg.id_float] + 1

                [p, q] = classifier.get_probability_distributions(new_msg.id_float,
                                                                  attack_seen_messages)

                current_entropy = classifier.calculate_entropy(attack_seen_messages)

                features.append([new_msg.id_float,
                                 classifier.find_num_occurrences_in_last_second(
                                     len(attack_msgs_parsed) - 1,
                                     new_msg.id_float,
                                     new_time_stamp,
                                     attack_msgs_parsed),
                                 classifier.calculate_relative_entropy(q, p),
                                 current_entropy - attack_previous_entropy,
                                 20])

                labels.append(1)

                attack_previous_entropy = current_entropy

                msg_types.append('DOS')

                if live_classification is True:
                    start = time.perf_counter()
                    prediction = classifier.prediction_wrapper(
                        attack_msgs_parsed[len(attack_msgs_parsed) - 1],
                        attack_msgs_parsed,
                        attack_seen_messages)
                    end = time.perf_counter()
                    op_analyzer.add_runtime(start, end, 'DOS')

                    if prediction is False:
                        output_str = 'Malicious message is ALLOWED'
                    else:
                        output_str = 'Malicious message is CAUGHT'
                    if print_test is True:
                        print(output_str)

                if attack_msgs_parsed[len(attack_msgs_parsed) - 1].timestamp \
                        - attack_msgs_parsed[0].timestamp \
                        >= max_log_interval:
                    attack_seen_messages[attack_msgs_parsed[0].id_float] -= 1
                    if attack_seen_messages[attack_msgs_parsed[0].id_float] == 0:
                        del attack_seen_messages[attack_msgs_parsed[0].id_float]
                    attack_seen_messages['Total'] -= 1
                    attack_msgs_parsed.popleft()

    print('Processed all data!')

    if train is True:
        classifier.train_classifier(features, labels)

    else:
        classifier.test_classifier(features, labels)

        predictions = classifier.predict_class(features)

        acc_analyzer = AccuracyAnalyzer(msg_types, labels, predictions)
        acc_analyzer.print_accuracy_statistics()

        if live_classification is True:
            op_analyzer.print_runtime_statistics('s')

        print()
        print('Message log size: ' + str(len(msgs_parsed)))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Please pass one command line argument to indicate which dataset to use. '
              'Available options:')
        for key in sorted(datasets.keys()):
            print('\t' + key)

        exit(1)

    selection = sys.argv[1]

    msg_classifier = MessageClassifier(datasets[selection]['model_dir'], verbose=True,
                                       probability_file=datasets[selection]['probability'])

    print('Training')
    main(msg_classifier, traffic_file=datasets[selection]['train'], train=True, print_test=False,
         live_classification=False, num_to_read=None, factor_to_read=None, skip_attacks=False)

    print('Validation')
    main(msg_classifier, traffic_file=datasets[selection]['test'], train=False, print_test=False,
         live_classification=False, num_to_read=None, factor_to_read=None, skip_attacks=False)
