"""Rules Library
provides rule inplementations for the rules based IDS

Notes:
    CAN Packet: a dict with 3 keys: timestamp, id, data
        timestamp is an int representing 0.1 milisecond intervals since start
        id is an 11-bit integer
        data is an 8-byte bytes object
"""

from preprocessor import id_past

# TODO: How to get infor for whitelists?


def id_whitelist(canlist):
    """Compares frame ID to whitelist"""
    pass


def time_interval(canlist):
    """Examines time interval between occurrence of known ID's
    To do this, it references a dictionary of acceptable time intervals
    """
    pass


def message_frequency(canlist):
    """Rule to detect DOS attacks
    This rule works by checking ID frequency and CAN bus bandwidth saturation.
    Notes:
        CAN Bus runs at 1e6 baud. So, bandwidth is about 10000 packets per
        second.
    """
    # rule thresholds
    size_req = 10
    max_id_per_sec = 300

    # TODO: check if there is better representation of results than list of
    # booleans

    # return True if sample is too small
    if len(canlist) < size_req:
        return [True for x in canlist]

    # check ID appearance frequency
    # TODO: check according to known frequency distrobutions
    id_counts = id_past(canlist)
    results = [x <= max_id_per_sec for x in id_counts]
    return results


def message_sequence(canlist):
    """Examines sequences of CAN packet ID's
    CAN packets of valid ID's are typically sent in a predicable sequence.
    This rule compares the input list against a list of known valid sequences.
    """
    pass


ROSTER = {
    'id_whitelist': id_whitelist,
    'time_interval': time_interval,
    'message_frequency': message_frequency,
    'message_sequence': message_sequence
}
