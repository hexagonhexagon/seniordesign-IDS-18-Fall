"""
Malicious Packet Generator
This is an interface to a library of attack generator functions.
These attacks will be used to train and test the IDS.
"""

import numpy

import malicious_generators


class MaliciousGenerator:
    """
    Manages malicious packet generators and their execution.

    Properties:
    - roster: Dict{ Name: Dict{ Attack, Probability } ... }
        This dictionary contains the attacks that can be used on the IDS. Each
        entry contains the probability of a certain attack, and the function
        pointer to get the packets.
        The malicious generator module contains its own roster, which this
        class will use as the default values.
        The sum of all probabilities should be == 1.
        - Attack: a function pointer to a malicious generator
            Usage: *func(scale)*
        - Probability: float
    """

    def __init__(self):
        self.roster = malicious_generators.ROSTER
        # FUTURE: import multiple modules, and adjust the probability of each
        # imported ROSTER, proportionally so that the total sum is 1
        assert sum([self.roster[x]['Probability'] for x in self.roster]) == 1.0

    def adjust(self, attack_name, new_prob):
        """
        Change the probability that a certain packet is returned from Get
        Malicious Packet.

        Arguments:
        - attack_name: string specifying which malicious generator to use
        - new_prob: the new probability the attack will have. All other attacks
          will have their probabilities adjusted proportionally, so that their
          sum == 1. This is the preferred way to set the Probability of an
          entry in the roster.
        """
        self.roster[attack_name]['Probability'] = new_prob
        other_sum = sum([
            self.roster[x]['Probability'] for x in self.roster
            if x != attack_name
        ])
        scaling_target = 1 - new_prob

        for item in self.roster:
            if item != attack_name:
                # normalize other probabilities to meet target
                self.roster[item]['Probability'] *= (
                    scaling_target / other_sum)

        assert sum([self.roster[x]['Probability'] for x in self.roster]) == 1.0

    def get(self, scale=1):
        """
        A generator function that uses the probabilities to return a malicious
        CAN frame or list of CAN frames to be injected into whatever is calling
        the function. Can return None, which indicates that no packet should be
        injected.

        Arguments:
        - scale: integer passed to the malicious generator.
          Specifies how many batches the generator should make. Should be 1
          packet per batch, for most.
        """
        choices = [self.roster[x]['Attack'] for x in self.roster]
        chances = [self.roster[x]['Probability'] for x in self.roster]
        chosen = numpy.random.choice(choices, p=chances)
        for _ in range(scale):
            for packet in chosen():
                yield packet

    def get_attack(self, attack_name, scale=1):
        """
        Uses the specified malicious generator to create a list of malicious
        packets.

        Arguments:
        - attack_name: string specifying which malicious generator to use
        - scale: integer passed to the malicious generator.
          Specifies how many batches the generator should make. Should be 1
          packet per batch, for most.
        """
        for _ in range(scale):
            for packet in self.roster[attack_name]['Attack']():
                yield packet
