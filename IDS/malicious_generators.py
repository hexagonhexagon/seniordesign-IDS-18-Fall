"""Malicious Generators
A library of malicious generator functions to be used by the MaliciousGenerator
class.

Module Constants:
- ROSTER: a dictionary containing references to each malicious generator
  contained in this module, and the default probabilities associated with each.
"""

# TODO: need a way to communicate with IDS to get info about the CAN bus.

import random


def random_packet(time_window):
    """Produces a CAN packet of random ID with random contents
    Args:
        time_window: subscriptable object containing two CAN packets
    """
    new_id = random.getrandbits(11)
    # new packet timestamp halfway between previous and next
    timestamp = int(time_window[0]['timestamp'] +
                    time_window[1]['timestamp']) / 2
    data = [random.getrandbits(8) for _ in range(8)]
    packet = {'timestamp': timestamp, 'id': new_id, 'data': data}
    yield packet


def flood(time_window):
    """Produces a long series of CAN packets
    Args:
        time_window: subscriptable object containing two CAN packets
    """
    new_id = 0
    timestamp = int(time_window[0]['timestamp'] +
                    time_window[1]['timestamp']) / 2
    data = [0, 0, 0, 0, 0, 0, 0, 0]
    packet = {'timestamp': timestamp, 'id': new_id, 'data': data}
    for _ in range(21):
        yield packet


def replay(time_window):
    """Reproduces the previous packet on the CAN bus
    Args:
        time_window: subscriptable object containing two CAN packets
    """
    # TODO: how to get last packet?


def spoof(time_window):
    """Create plausible message data of a known ID
    Args:
        time_window: subscriptable object containing two CAN packets
    """
    # TODO: which ID?


ROSTER = {
    'random': {
        'attack': random_packet,
        'probability': 0.25
    },
    'flood': {
        'attack': flood,
        'probability': 0.25
    },
    'replay': {
        'attack': replay,
        'probability': 0.25
    },
    'spoof': {
        'attack': spoof,
        'probability': 0.25
    }
}
