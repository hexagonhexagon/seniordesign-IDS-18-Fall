"""Malicious Generators
A library of malicious generator functions to be used by the MaliciousGenerator
class.

Module Constants:
- ROSTER: a dictionary containing references to each malicious generator
  contained in this module, and the default probabilities associated with each.

Notes:
    CAN Packet: a dict with 3 keys: timestamp, id, data
        timestamp is an int representing 0.1 milisecond intervals since start
        id is an 11-bit integer
        data is an 8-byte bytes object
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
    timestamp = int(
        (time_window[0]['timestamp'] + time_window[1]['timestamp']) / 2)
    data = bytes([random.getrandbits(8) for _ in range(8)])
    packet = {'timestamp': timestamp, 'id': new_id, 'data': data}
    yield packet


def flood(time_window):
    """Produces a long series of CAN packets
    Args:
        time_window: subscriptable object containing two CAN packets
    """
    new_id = 0
    n_to_make = 21
    timestamp_step = (time_window[1]['timestamp']
                    - time_window[0]['timestamp']) / n_to_make
    data = bytes([0, 0, 0, 0, 0, 0, 0, 0])
    for ii in range(n_to_make):
        timestamp = int(time_window[0]['timestamp'] + timestamp_step * ii)
        packet = {'timestamp': timestamp, 'id': new_id, 'data': data}
        yield packet


def replay(time_window):
    """Reproduces the previous packet on the CAN bus
    Args:
        time_window: subscriptable object containing two CAN packets
    """
    yield time_window[0]


def spoof(time_window):
    """Create plausible message data of a known ID
    Args:
        time_window: subscriptable object containing two CAN packets
    """
    # TODO: which ID?
    #       what data?

    new_id = 0
    timestamp = int(
        (time_window[0]['timestamp'] + time_window[1]['timestamp']) / 2)
    data = bytes([0, 0, 0, 0, 0, 0, 0, 0])
    packet = {'timestamp': timestamp, 'id': new_id, 'data': data}
    yield packet


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
