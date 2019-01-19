"""Rules Library
provides rule inplementations for the rules based IDS

See rule_abc.Rule for definitions of how Rules should behave

Notes:
    CAN Packet: a dict with 3 keys: timestamp, id, data
        timestamp is an int representing 0.1 milisecond intervals since start
        id is an 11-bit integer
        data is an 8-byte bytes object
"""

import collections
import json
import numpy as np
import IDS.preprocessor
from IDS.rule_abc import Rule
from statistics import stdev, mean


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
    Acceptable time intervals will be calculated for each CAN ID, by choosing
    the K most numerous bins of a histogram of the time intervals.

    Attributes:
        num_bins: integer indicating how many bins to use in the histogram.
        This effectively sets the precision of the rule. See
        numpy.histogram_bin_edges. if num_bins is 'auto' a bin count will be
        calculated and be assigned to num_bins by prepare().

        num_selections: an integer representing the number of most common
        clusters to be choosen as valid. must be 0 < x < num_bins

        
    Notes:
        num_bins and num_selections are only valid before prepare() is run.
    """

    def __init__(self, profile_id):
        super().__init__(self, profile_id)
        self.num_bins = 'auto'
        self.num_selections = 10

    @property
    def num_selections(self):
        return self.__num_selections

    @num_selections.setter
    def num_selections(self, x):
        if x < 1:
            self.__num_selections = 1
        elif isinstance(self.num_bins, int) and x >= self.num_bins:
            self.__num_selections = self.num_bins - 1
        else:
            self.__num_selections = x

    def _delays(self, canlist):
        """Calculate delay from last occurrence for each CAN packet
        Delay for first encounter of each ID is -1.
        Returns:
            Python generator yielding time delays as floats.
        """
        last_id = {}
        for pak in canlist:
            if pak['id'] not in last_id:
                yield -1
            else:
                yield pak['timestamp'] - last_id[pak['id']]
            last_id[pak['id']] = pak['timestamp']

    def test(self, canlist):
        """Check that delays between packet ID's are acceptable
        see Rule.test
        """
        delays = self._delays(canlist)
        for delay, can_id in zip(delays, (x['id'] for x in canlist)):
            if can_id not in self.known_delays:
                yield False
            elif delay == -1:
                yield True
            elif np.digitize(delay, self.bins[can_id]) \
                    in self.valid_bins[can_id]:
                yield True
            else:
                yield False

    def prepare(self, canlist=None):
        """Calculate acceptable delay values
        Working Data:
            bins: list representing ranges to sort time intervals into.

            valid_bins: a list of indicies, corresponding to `bins` that are
            considered valid time intervals.

        see Rule.prepare
        """
        if canlist:
            # Sort time intervals by packet ID
            id_delays = collections.defaultdict(list())
            delays = self._delays(canlist)
            for delay, can_id in zip(delays, (x['id'] for x in canlist)):
                id_delays[can_id].append(delay)

            # Make histograms for each ID's delay list
            for can_id, delays in id_delays.items():
                hist, self.bins[can_id] = np.histogram(delays, self.num_bins)
                if self.num_bins == 'auto':
                    num_sel = int(len(hist) / 10) + 1
                else:
                    num_sel = self.num_selections
                # Get the indicies of K largest values
                self.valid_bins[can_id] = set(hist.argsort()[-num_sel:])

            savedata = {
                'bins': self.bins,
                'valid_bins': self.valid_bins,
            }
            with self.save_file.open('w') as prof:
                json.dump(savedata, prof)
        else:
            super()._load()
            # JSON doesn't support python sets
            self.valid_bins = {x: set(y) for x, y in self.valid_bins.items()}


class MessageFrequency(Rule):
    """Rule to detect DOS attacks
    This rule works by checking ID frequency and CAN bus bandwidth saturation.
    Notes:
        CAN packet timestamp is in 0.1 milisecond intervals

    Attributes:
        time_frame: a float value in miliseconds, representing the calculation
        window for message frequencies.
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
        id_counts = IDS.preprocessor.id_past(canlist, self.time_frame)
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
            id_counts = IDS.preprocessor.id_past(canlist, self.time_frame)
            self.frequencies = collections.defaultdict(list())
            for count, can_id in zip(id_counts, (x['id'] for x in canlist)):
                self.frequencies[can_id].append(count)

            for can_id, c_list in self.frequencies.items():
                c_std = stdev(c_list)
                c_mean = mean(c_list)
                self.frequencies[can_id] = (c_mean - 2 * c_std,
                                            c_mean + 2 * c_std)

            savedata = {
                'frequencies': self.frequencies,
                'time_frame': self.time_frame
            }
            with self.save_file.open('w') as prof:
                json.dump(savedata, prof)
        else:
            super()._load()


class MessageSequence(Rule):
    """Examines sequences of CAN packet ID's
    CAN packets of valid ID's are typically sent in a predicable sequence.
    This rule compares the input list against a list of known valid sequences.

    Attributes:
        length: an integer representing the number of CAN packets to be
        considered in a sequence.
    """

    def __init__(self, profile_id, length=5):
        """Init Message Sequence
        Length in number of packets
        """
        super().__init__(self, profile_id)
        self.length = length

    def test(self, canlist):
        """Check packet sequences
        Marks true for first packets within sequence length.
        """
        for ii, _ in enumerate(canlist):
            if ii < self.length:
                yield True
                continue
            seq = tuple(
                canlist[ii - x]['id'] for x in reversed(range(0, self.length)))
            yield seq in self.sequences

    def prepare(self, canlist=None):
        """Create set of allowed sequences
        The set will be represented as a python set containing tuples.
        """
        if canlist:
            self.sequences = set()
            for ii, _ in enumerate(canlist):
                if ii < self.length:
                    continue
                seq = tuple(canlist[ii - x]['id']
                            for x in reversed(range(0, self.length)))
                self.sequences.add(seq)

            savedata = {
                # can't save a set with JSON
                'sequences': list(self.sequences),
                'length': self.length
            }
            with self.save_file.open('w') as prof:
                json.dump(savedata, prof)
        else:
            super()._load()
            # set lookups are much faster than lists: O(1) vs O(n)
            self.sequences = set(tuple(x) for x in self.sequences)


ROSTER = {
    'ID_Whitelist': ID_Whitelist,
    # 'TimeInterval': TimeInterval,
    'MessageFrequency': MessageFrequency,
    'MessageSequence': MessageSequence
}
