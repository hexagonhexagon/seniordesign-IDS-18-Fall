"""
Malicious Generators
A library of malicious generator functions to be used by the MaliciousGenerator
class.

Module Constants:
- ROSTER: a dictionary containing references to each malicious generator
  contained in this module, and the default probabilities associated with each.
"""

# TODO: need a way to communicate with IDS to get info about the CAN bus.

import numpy as np

def random_packet():
    """
    Produces a CAN packet of random ID with random contents
    """
    # format string is zero-pad, 5 chars long, convert to hex uppercase letters
    new_id = "{0:#0{1}X}".format(np.random.randint(0, 2048), 5)[2:]

    # TODO: How to get next timestamp?
    # new_time_stamp = (can_msgs[i].timestamp + can_msgs[i + 1].timestamp) / 2
    timestamp = np.random.randint(0, 1e9)

    data = [np.random.randint(0, 256) for _ in range(8)]
    packet = {'Timestamp': timestamp, 'ID': new_id, 'Data': data}
    yield packet


def flood():
    """
    Produces a long series of CAN packets
    """
    new_id = '000'
    timestamp = 0
    data = [0, 0, 0, 0, 0, 0, 0, 0]
    packet = {'Timestamp': timestamp, 'ID': new_id, 'Data': data}
    for _ in range(21):
        yield packet


def replay():
    """
    Reproduces the previous packet on the CAN bus
    """
    # TODO: how to get last packet?


def spoof():
    """
    Create plausible message data of a known ID
    """
    # TODO: which ID?


ROSTER = {
    'random': {
        'Attack': random_packet,
        'Probability': 0.25
    },
    'flood': {
        'Attack': flood,
        'Probability': 0.25
    },
    'replay': {
        'Attack': replay,
        'Probability': 0.25
    },
    'spoof': {
        'Attack': spoof,
        'Probability': 0.25
    }
}
