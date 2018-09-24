import json
import math
import os
import sys
import logging

import numpy as np

from NNIDS.canclass import CANMessage
from NNIDS.classifier_impl import MessageClassifier
from NNIDS.parsers import log

from attacks.log import attack1
from rules.log import rule1

if msg_types[i] == 'Valid':
    num_valid += 1
    if int(predictions[i][0]) == 0:
        num_valid_caught += 1

 for i in range(0, len(can_msgs)):
        # if i == 100:
        #     break
        if (i - 1) % 10000 == 0:
            print('Processed ' + str(i - 1) + ' of ' + str(len(can_msgs)))

        msgs_parsed.append(can_msgs[i])

        seen_messages['Total'] = seen_messages['Total'] + 1

        rand_num = np.random.randint(0, 24)
        if i < len(can_msgs) - 1 and rand_num == 0:
            rand_id = '000'
            new_time_stamp = (can_msgs[i].timestamp + can_msgs[i + 1].timestamp) / 2

            new_msg = CANMessage(new_time_stamp, rand_id, 0)
            msgs_parsed.append(new_msg)