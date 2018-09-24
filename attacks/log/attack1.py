import json
import math
import os
import sys
import logging

import numpy as np

from NNIDS.canclass import CANMessage
from NNIDS.classifier_impl import MessageClassifier
from NNIDS.parsers import log

rand_id = "{0:#0{1}X}".format(np.random.randint(0, 4096), 5)[2:]
new_time_stamp = (can_msgs[i].timestamp + can_msgs[i + 1].timestamp) / 2

new_msg = CANMessage(new_time_stamp, rand_id, 0)
msgs_parsed.append(new_msg)

seen_messages['Total'] = seen_messages['Total'] + 1
if new_msg.id_float not in seen_messages:
    seen_messages[new_msg.id_float] = 0
seen_messages[new_msg.id_float] = seen_messages[new_msg.id_float] + 1

[p, q] = get_probability_distributions(new_msg.id_float, known_messages,
                                       seen_messages)
current_entropy = calculate_entropy(seen_messages)
features.append([new_msg.id_float,
                 find_num_occurrences_in_last_second(len(msgs_parsed) - 1,
                                                     new_msg.id_float,
                                                     new_time_stamp, msgs_parsed),
                 calculate_relative_entropy(q, p), current_entropy - previous_entropy,
                 20])
labels.append(1)

msg_types.append('Random injection')

if print_test is True:
    prediction = classifier.prediction_wrapper(msgs_parsed[len(msgs_parsed) - 1],
                                               msgs_parsed,
                                               seen_messages)
    if prediction is False:
        output_str = 'Malicious message is ALLOWED'
    else:
        output_str = 'Malicious message is CAUGHT'
    print(output_str)




def attack1():
        if i < len(can_msgs) - 1 and rand_num == 0:
            rand_id = '000'
            new_time_stamp = (can_msgs[i].timestamp + can_msgs[i + 1].timestamp) / 2

            new_msg = CANMessage(new_time_stamp, rand_id, 0)
            msgs_parsed.append(new_msg)