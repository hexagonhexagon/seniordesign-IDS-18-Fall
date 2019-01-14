"""Rules Library
provides rule inplementations for the rules based IDS

Notes:
    CAN Packet: a dict with 3 keys: timestamp, id, data
        timestamp is an int representing 0.1 milisecond intervals since start
        id is an 11-bit integer
        data is an 8-byte bytes object
"""

from preprocessor import id_past
from rule_abc import Rule


class ID_Whitelist(Rule):
    """Compares frame ID to whitelist"""
    pass


class TimeInterval(Rule):
    """Examines time interval between occurrence of known ID's
    To do this, it references a dictionary of acceptable time intervals
    """
    pass


class MessageFrequency(Rule):
    """Rule to detect DOS attacks
    This rule works by checking ID frequency and CAN bus bandwidth saturation.
    Notes:
        CAN Bus runs at 1e6 baud. So, bandwidth is about 10000 packets per
        second.
    """
    def __init__(self, profile_id):
        super().__init__(profile_id)

    def test(self, canlist):
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


class MessageSequence(Rule):
    """Examines sequences of CAN packet ID's
    CAN packets of valid ID's are typically sent in a predicable sequence.
    This rule compares the input list against a list of known valid sequences.
    """
    pass


PREP = {

}


ROSTER = {
    'ID_Whitelist': ID_Whitelist,
    'TimeInterval': TimeInterval,
    'MessageFrequency': MessageFrequency,
    'MessageSequence': MessageSequence
}
