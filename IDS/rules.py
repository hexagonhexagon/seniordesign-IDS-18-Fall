"""Rules Library
provides rule inplementations for the rules based IDS

See rule_abc.Rule for definitions of how Rules should behave

Notes:
    CAN Packet: a dict with 3 keys: timestamp, id, data
        timestamp is an int representing 0.1 millisecond intervals since start
        id is an 11-bit integer
        data is an 8-byte bytes object

    Test Results are bools representing "is_malicious" for each CAN frame
"""
import collections
from statistics import mean, stdev

import numpy as np

import IDS.preprocessor
from IDS.rule_abc import Rule


class ID_Whitelist(Rule):
    """Compares frame ID to whitelist"""

    def __init__(self, profile_id):
        super().__init__(profile_id)
        self.whitelist = set()

    def _reset(self):
        """Reset Rule's working data"""
        self.whitelist = set()

    def test(self, canlist):
        """Check against whitelist
        see Rule.test
        """
        super().test(canlist)
        for pak in canlist:
            yield pak['id'] not in self.whitelist

    def prepare(self, canlist=None):
        """Compile whitelist from CAN data, or import existing profile.
        See Rule.prepare
        """
        if canlist:
            self._reset()
            # make new set of valid ID's
            self.whitelist = set(x['id'] for x in canlist)
            savedata = {'whitelist': list(self.whitelist)}
            super()._save(savedata)
        else:
            # load existing profile data
            super()._load()
            # JSON doesn't support sets
            self.whitelist = set(self.whitelist)

        self._is_prepared = True


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

        coverage: ratio of data held by the indices of valid_bins to data
        observed in histogram.

        Working Data:
        bins: array where each value represents the edge of a bin for the
        histogram.
        valid_bins: a list of integers corresponding to indices of `bins`.

    Notes:
        num_bins and num_selections are only valid before prepare() is run.
    """

    def __init__(self, profile_id):
        super().__init__(profile_id)
        self.num_bins = 'auto'
        self.__coverage = 1.0
        # init empty working data
        self.bins = {}
        self.valid_bins = collections.defaultdict(set)

    def _reset():
        """Reset rule's working data"""
        self.bins = {}
        self.valid_bins = collections.defaultdict(set)

    @property
    def coverage(self):
        """coverage must be 0 < x < 1"""
        return self.__coverage

    @coverage.setter
    def coverage(self, val):
        if val > 1.0:
            self.__coverage = 1.0
        elif val < 0.0:
            self.__coverage = 0.0
        else:
            self.__coverage = val

    @staticmethod
    def _delays(canlist):
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
        super().test(canlist)

        delays = self._delays(canlist)
        for delay, pak in zip(delays, canlist):
            can_id = pak['id']
            if can_id not in self.valid_bins:
                yield True
            elif delay == -1:
                yield False
            elif int(np.digitize(delay, self.bins[can_id])) \
                    in self.valid_bins[can_id]:
                yield False
            else:
                yield True

    def prepare(self, canlist=None):
        """Calculate acceptable delay values
        Working Data:
            bins: list representing ranges to sort time intervals into.

            valid_bins: a list of indices, corresponding to `bins` that are
            considered valid time intervals.

        see Rule.prepare
        """
        if canlist:
            self._reset()
            # Sort time intervals by packet ID
            id_delays = collections.defaultdict(list)
            delays = self._delays(canlist)
            for delay, pak in zip(delays, canlist):
                id_delays[pak['id']].append(delay)

            # Make histograms for each ID's delay list
            for can_id, delays in id_delays.items():
                hist, hist_bins = np.histogram(delays, self.num_bins)
                # JSON can't handle numpy datatypes
                self.bins[can_id] = [float(x) for x in hist_bins]

                # Add indicies of the histogram, from largest to smallest,
                # until a suitable level of data coverage is reached.
                hist_inds = hist.argsort()
                valid_bins_coverage = 0.0
                for ind in hist_inds:
                    if valid_bins_coverage >= self.coverage:
                        break
                    self.valid_bins[can_id].add(int(ind))
                    valid_bins_coverage += hist[ind]
                # JSON can't handle numpy datatypes

            savedata = {
                'bins': self.bins,
                'valid_bins': {x: list(y)
                               for x, y in self.valid_bins.items()},
            }
            super()._save(savedata)
        else:
            super()._load()
            # JSON doesn't support python sets
            # JSON saves all keys as strings
            self.bins = {int(x): y for x, y in self.bins.items()}
            self.valid_bins = {
                int(x): set(y)
                for x, y in self.valid_bins.items()
            }

        self._is_prepared = True


class MessageFrequency(Rule):
    """Rule to detect DOS attacks
    This rule works by checking ID frequency and CAN bus bandwidth saturation.
    Notes:
        CAN packet timestamp is in 0.1 millisecond intervals

    Attributes:
        time_frame: a float value in seconds, representing the calculation
        window for message frequencies.
    """

    def __init__(self, profile_id):
        """Init MessageFrequency Rule
        Set Time Window in seconds
        """
        super().__init__(profile_id)
        self.time_frame = 1
        self.frequencies = collections.defaultdict(list)

    def _reset(self):
        """Resets rule working data."""
        self.frequencies = collections.defaultdict(list)

    def test(self, canlist):
        """Check that packet occurrence is within acceptable frequencies.
        see Rule.test
        """
        super().test(canlist)

        # return True if sample is too small
        if len(canlist) < self.time_frame * 1e4:
            yield from (False for x in canlist)
            return

        # check ID appearance frequency
        id_counts = IDS.preprocessor.ID_Past(self.time_frame).feed(canlist)
        for count, pak in zip(id_counts, canlist):
            can_id = pak['id']
            if can_id not in self.frequencies:
                yield True
                continue
            low, high = self.frequencies[can_id]
            if low <= count <= high:
                yield False
            else:
                yield True

    def prepare(self, canlist=None):
        """Create frequency range dictionary
        Frequency dict keys are CAN packet ID's.
        Frequemcy range is Observed range +- Std.Dev. This is stored as a
        tuple.

        if no CAN data provided, load existing profile data.
        see Rule.prepare
        """
        if canlist:
            self._reset()
            id_counts = IDS.preprocessor.ID_Past(self.time_frame).feed(canlist)
            for count, pak in zip(id_counts, canlist):
                can_id = pak['id']
                self.frequencies[can_id].append(count)

            new_freq = collections.defaultdict(list)
            for can_id, c_list in self.frequencies.items():
                if len(c_list) > 1:
                    c_std = stdev(c_list)
                    c_mean = mean(c_list)
                    new_freq[can_id] = (c_mean - 2 * c_std, c_mean + 2 * c_std)
            self.frequencies = new_freq

            savedata = {
                'frequencies': self.frequencies,
                'time_frame': self.time_frame
            }
            super()._save(savedata)
        else:
            super()._load()
            # JSON saves all keys as strings
            self.frequencies = {
                int(x): tuple(y)
                for x, y in self.frequencies.items()
            }

        self._is_prepared = True


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
        super().__init__(profile_id)
        self.length = length
        self.sequences = set()

    def _reset(self):
        """Resets rule working data"""
        self.sequences = set()

    def test(self, canlist):
        """Check packet sequences
        Marks true for first packets within sequence length.
        Uses a queue to sample sequences; the queue is 'rolled back' one, if a
        bad packet is appended to the queue.
        Initial sequence can get corrupted if bad values are present during
        filling. Using a sample from valid sequence list to prevent initial
        sequence corruption.

        Note: if sequence sampling gets corrupted, rule will reject all packets
        """
        super().test(canlist)

        # using a sample from valid sequences to prime the initial sequence.
        seq = collections.deque(next(iter(self.sequences)))  # left is old
        prev = None
        for pak in canlist:
            seq.append(pak['id'])
            prev = seq.popleft()

            if tuple(seq) in self.sequences:
                yield False
            else:
                # get rid of bad value from sequence
                seq.appendleft(prev)
                seq.pop()
                yield True

    def prepare(self, canlist=None):
        """Create set of allowed sequences
        The set will be represented as a python set containing tuples.
        """
        if canlist:
            self._reset()
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
            super()._save(savedata)
        else:
            super()._load()
            # set lookups are much faster than lists: O(1) vs O(n)
            self.sequences = set(tuple(x) for x in self.sequences)

        self._is_prepared = True


ROSTER = {
    'ID_Whitelist': ID_Whitelist,
    'TimeInterval': TimeInterval,
    'MessageFrequency': MessageFrequency,
    'MessageSequence': MessageSequence
}
