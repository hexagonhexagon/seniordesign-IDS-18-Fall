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
import preprocessor
from rule_abc import Rule
from statistics import stdev


class ID_Whitelist(Rule):
    """Compares frame ID to whitelist"""

    def test(self, canlist):
        """Check against whitelist
        see Rule.test
        """
        for can_id in (x['id'] for x in canlist):
            yield can_id in self.whitelist

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
        CAN packet timestamp is in 0.1 milisecond intervals
    """

    def __init__(self, profile_id, time_frame=1000):
        """Init MessageFrequency Rule
        Set Time Window in miliseconds
        """
        super().__init__(self, profile_id)
        self.time_frame = time_frame

    def test(self, canlist):
        """Check that packet occurrence is within acceptable frequencies.
        see Rule.test
        """
        # return True if sample is too small
        if len(canlist) < self.time_frame * 10:
            yield from (True for x in canlist)
            return

        # check ID appearance frequency
        id_counts = preprocessor.id_past(canlist, self.time_frame)
        for count, can_id in zip(id_counts, (x['id'] for x in canlist)):
            if can_id not in self.frequencies:
                yield False
                continue
            low, high = self.frequencies[can_id]
            if low <= count <= high:
                yield True
            else:
                yield False

    def prepare(self, canlist=None):
        """Create frequency range dictionary
        Frequency dict keys are CAN packet ID's.
        Frequemcy range is Observed range +- Std.Dev. This is stored as a
        tuple.

        if no CAN data provided, load existing profile data.
        see Rule.prepare
        """
        if canlist:
            id_counts = preprocessor.id_past(canlist, self.time_frame)
            self.frequencies = {x['id']: list() for x in canlist}
            for count, can_id in zip(id_counts, (x['id'] for x in canlist)):
                self.frequencies[can_id].append(count)
            for can_id, c_list in self.frequencies.items():
                c_std = stdev(c_list)
                c_min = min(c_list)
                c_max = max(c_list)
                self.frequencies[can_id] = (c_min - c_std, c_max + c_std)

            with self.save_file.open('w') as prof:
                json.dump({'frequencies': self.frequencies}, prof)
        else:
            super()._load()


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
