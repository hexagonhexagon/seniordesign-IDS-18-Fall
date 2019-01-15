"""Rules Library
provides rule inplementations for the rules based IDS

See rule_abc.Rule for definitions of how Rules should behave

Notes:
    CAN Packet: a dict with 3 keys: timestamp, id, data
        timestamp is an int representing 0.1 milisecond intervals since start
        id is an 11-bit integer
        data is an 8-byte bytes object
"""

import json
from preprocessor import id_past
from rule_abc import Rule


class ID_Whitelist(Rule):
    """Compares frame ID to whitelist"""

    def test(self, canlist):
        """Check against whitelist"""
        return [x['id'] in self.whitelist for x in canlist]

    def prepare(self, canlist=None):
        """Compile whitelist from CAN data, or import existing profile.
        See Rule.prepare
        """
        if canlist:
            # make new set of valid ID's
            self.whitelist = set(x['id'] for x in canlist)
            # self.save_file defined by Rule (parent)
            with self.save_file.open('w') as prof:
                json.dump({'whitelist': self.whitelist}, prof)
        else:
            # load existing profile data
            super()._load()


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


ROSTER = {
    'ID_Whitelist': ID_Whitelist,
    'TimeInterval': TimeInterval,
    'MessageFrequency': MessageFrequency,
    'MessageSequence': MessageSequence
}
