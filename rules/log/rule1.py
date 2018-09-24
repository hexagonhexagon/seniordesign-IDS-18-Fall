import json
import math
import os
import sys
import logging

import numpy as np

from NNIDS.canclass import CANMessage
from NNIDS.classifier_impl import MessageClassifier
from NNIDS.parsers import log

wd = os.getcwd()
probability_file = 'data/analysis_dump/id_occurrences.json'
rec_2 = wd + '/data/logs/recording2.log'
rec_1 = wd + '/data/logs/recording1.log'
known_messages = {}
msg_types = []
can_msgs = log.log_parser(rec_2)
with open(probability_file, 'r') as infile:
    temp_msgs = json.load(infile)
    for key in temp_msgs:
        known_messages[int(key, 16)] = temp_msgs[key]

 for i in range(0, len(can_msgs)):
        # if i == 100:
        #     break
        if (i - 1) % 10000 == 0:
            print('Processed ' + str(i - 1) + ' of ' + str(len(can_msgs)))

        msgs_parsed.append(can_msgs[i])

        seen_messages['Total'] = seen_messages['Total'] + 1

        rand_num = np.random.randint(0, 25)
        if i < len(can_msgs) - 1 and rand_num == 0:
            rand_id = '000'
            new_time_stamp = (can_msgs[i].timestamp + can_msgs[i + 1].timestamp) / 2

            new_msg = CANMessage(new_time_stamp, rand_id, 0)
            msgs_parsed.append(new_msg)
if can_msgs[i] in known_messages:

for known_id in known_messages:
    if count == rand_idx:
        rand_id = known_id
        break
    count += 1

