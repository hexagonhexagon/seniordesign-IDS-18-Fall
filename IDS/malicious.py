"""
Malicious Packet Generator
This is an interface to a library of attack generator functions.
These attacks will be used to train and test the IDS.

Attributes:
    NONE_ROSTER: a partial roster kept in this module, to define the default
    probability for returning nothing on get. This will be merged with the
    roster imported from malicious_generators
"""

import random
from math import isclose  # used to compare floats

import malicious_generators

NONE_ROSTER = {'none': {'attack': None, 'probability': 0.5}}


class MaliciousGenerator:
    """Manages malicious packet generators and their execution.

    Attributes:
    - roster: Dict{ Name: Dict{ attack, probability } ... }
        This dictionary contains the attacks that can be used on the IDS. Each
        entry contains the probability of a certain attack, and the function
        pointer to get the packets.
        The malicious generator module contains its own roster, which this
        class will use as the default values.
        The sum of all probabilities should be == 1.
        - attack: a function pointer to a malicious generator
            Usage: *func(scale)*
        - probability: float
    """

    def __init__(self):
        """Initializes class by importing roster from malicious_generators.

        Raises:
            AssertionError:: roster probabilities not set correctly; need == 1
        """
        # MAYBE: import multiple modules with malicious_generators
        self.roster = malicious_generators.ROSTER
        self.roster.update(NONE_ROSTER)  # add to roster
        self._normalize_roster()

        self.check_roster()

    def check_roster(self):
        """Checks roster attribute for validity

        Raises:
            AssertionError:: roster probabilities not set correctly; need == 1
        """
        prob_sum = sum([self.roster[x]['probability'] for x in self.roster])
        assert isclose(prob_sum, 1.0)

    def _normalize_roster(self):
        """Normalizes probability values in roster, by adjusting each value
        proportionally so that the sum is 1
        """
        prob_sum = sum([self.roster[x]['probability'] for x in self.roster])
        for item in self.roster:
            self.roster[item]['probability'] *= (1 / prob_sum)
        self.check_roster()

    def adjust(self, adjustments):
        """Change the probability that a certain packet is returned from Get
        Malicious Packet.

        Arguments:
        - adjustments: Dict specifying the attacks and their new probabilities.
            All other attacks will have their probabilities adjusted
            proportionally, so that the sum == 1. This is the preferred way
            to set the probability of an entry in the roster.

        Raises:
            AssertionError:: if adjustments sum outside [0,1]

        Examples:
            >>> mal = MaliciousGenerator()
            >>> mal.adjust({'random': 0.5})
            >>> mal.adjust({'random': 0.3, 'spoof': 0.2})
        """
        scaling_target = 1 - sum(x for x in adjustments.values())
        assert 0 <= scaling_target <= 1

        other_sum = sum([
            self.roster[x]['probability'] for x in self.roster
            if x not in adjustments
        ])

        for item in self.roster:
            if item in adjustments:
                self.roster[item]['probability'] = adjustments[item]
            elif other_sum == 0:
                self.roster[item]['probability'] += \
                    scaling_target / (len(self.roster) - len(adjustments))
            else:
                # normalize other probabilities to meet target
                self.roster[item]['probability'] *= (
                    scaling_target / other_sum)

        self.check_roster()

    def get(self, time_window, repeat=1):
        """A generator function that uses the probabilities to return a
        malicious CAN frame or list of CAN frames to be injected into whatever
        is calling the function. Can return None, which indicates that no
        packet should be injected.

        Arguments:
          - time_window: a subscriptable object containing two packets.
          - repeat: integer passed to the malicious generator.
            Specifies how many batches the generator should make. Should be 1
            packet per batch, for most.

        Returns:
            python generator object yielding 0 to N CAN packets.
            A CAN packet is a dict with keys 'timestamp', 'id', and 'data'

        Usage: 
            mal.get() is as python generator, a kind of iterable object.
            A single value can be returned using the next() funciton.
            next() will raise a StopIteration error when the generator exits,
            unless the `default` argument is set.
            Another use is `for x in mal.get()` as used in a loop or list
            comprehension.

        Examples:
            >>> mal = MaliciousGenerator()
            >>> next(mal.get((pak1,pak2)))
            {'timestamp': 5,
                'id': 1433,
                'data': [145, 49, 247, 135, 200, 57, 54, 214]}
            >>> [x for x in mal.get([pak1, pak2], 2)]
            [{'timestamp': 5,
                'id': 1433,
                'data': [145, 49, 247, 135, 200, 57, 54, 214]},
            {'timestamp': 5,
                'id': 1433,
                'data': [145, 49, 247, 135, 200, 57, 54, 214]}]
        """
        choices = [self.roster[x]['attack'] for x in self.roster]
        chances = [self.roster[x]['probability'] for x in self.roster]
        chosen = random.choices(choices, weights=chances)[0]
        if chosen is None:
            return
        for _ in range(repeat):
            for packet in chosen(time_window):
                yield packet

    def get_attack(self, time_window, attack_name, repeat=1):
        """
        Uses the specified malicious generator to create a list of malicious
        packets.

        Arguments:
          - time_window: a subscriptable object containing two packets.
          - attack_name: string specifying which malicious generator to use
          - repeat: integer passed to the malicious generator.
            Specifies how many batches the generator should make. Should be 1
            packet per batch, for most.

        Returns:
            python generator object yielding 1 to N CAN packets.
            A CAN packet is a dict with keys 'timestamp', 'id', and 'data'

        Usage:
            Same as for MaliciousGenerator.get(), but with `attack_name`
            argument.

        Raises:
            TypeError: when attack_name == 'none'
            KeyError:  when attack_name doesn't match any keys in the roster
        """
        for _ in range(repeat):
            for packet in self.roster[attack_name]['attack'](time_window):
                yield packet
