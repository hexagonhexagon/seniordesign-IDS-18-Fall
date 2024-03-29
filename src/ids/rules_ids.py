"""Rules based IDS
This module provides a class to examine CAN packets using rules and heuristics.
The implementations of rules used, will be loaded from another module, rules.py

Notes:
    The imported module, rules, provides:
    ROSTER: a dictionary containing function pointers to the rules.
    Each function accepts a CAN packet as input.
    The rule implementations are being imported from a separate module to allow
    for easy plug-in ability for rules. Note that this allows for execution of
    arbitrary code.
"""

import ids.rules
import ids.rule_abc
import collections.abc


class RulesIDS:
    """Examine CAN packets according to a set of rules."""

    def __init__(self, profile_id=None):
        """Init IDS
        """
        self.profile_id = profile_id
        self.roster = ids.rules.ROSTER
        self.__is_prepared = False

    @property
    def is_prepared(self):
        return self.__is_prepared
    # is_prepared does not have a setter

    @property
    def profile_id(self):
        return self.__profile_id

    @profile_id.setter
    def profile_id(self, val):
        self.__is_prepared = False
        self.__profile_id = val

    def prepare(self, canlist=None, set_profile_id=None):
        """Prepare rule heuristics with working data
        Some rules require whitelists or other such data for their operation.
        This function will instantiate the classes provided in self.roster, and
        run their "prepare" methods, if available.

        Args:
            canlist (optional): a list of clean CAN packets to develop Rule
            Heuristics. If not set, the rules will check for existing profile
            data.

            set_profile_id (optional): string identifying CAN profile (e.g.
            Ford_Fusion_2018). This is optional for this call, but
            self.profile_id must be set for the function to run. It can either
            be set in __init__, through direct assignment, or as an argument in
            this call.

        Raises:
            ValueError: when profile_id is not set
            ValueError: when a value in self.roster is not a Rule
            FileNotFoundError: if rules not instantiated with CAN data, and
            can't find existing profile data.
        """
        if set_profile_id:
            self.profile_id = set_profile_id
        if not self.profile_id:
            raise ValueError("IDS Profile not set")

        # Instantiate rules
        # Each item in roster should be a class definition deriving from
        # rule_abc.Rule
        new_roster = {}
        for name, rule in self.roster.items():
            # instantiate contained class if not already
            if not isinstance(rule, ids.rule_abc.Rule):
                rule = rule(self.profile_id)
            rule.profile_id = self.profile_id
            rule.prepare(canlist)
            new_roster[name] = rule
        self.roster = new_roster
        self.__is_prepared = True

    def test(self, can_frame):
        """Examine single CAN packet according to rules in the roster
        Args:
            can_frame: a single CAN packet

        Returns:
            Tuple (bool, str)
            Returns on the first rule to fail, with str as the name of the rule
            that failed the packet. Else, str is None. bool represents
            "is_malicious".

        Raises:
            TypeError: if can_frame isn't like a dict
            ValueError: if rules have not been prepared.
        """
        if not self.is_prepared:
            raise ValueError("Rules are not prepared.")
        if not isinstance(can_frame, collections.abc.Mapping):
            raise TypeError('can_frame must be like a dictionary')

        for name, rule in self.roster.items():
            # Each rule is a generator yielding booleans for a list sent in.
            result = next(rule.test([can_frame]))
            if result:
                return True, name
        return False, None

    def test_series(self, canlist):
        """Examine list of CAN packets according to rules in the roster
        Args:
            canlist: a list of CAN packets

        Returns:
            A python generator yieldinga tuples (bool, name).
            Each tuple corresponds to a packet in the input list.
            str is the name of the rule to first fail a given packet, or None
            if passed. bool represents "is_malicious".

        Raises:
            TypeError: if canlist isn't like a list
            ValueError: if rules have not been prepared.
        """
        if not self.is_prepared:
            raise ValueError("Rules are not prepared.")
        if not isinstance(canlist, collections.abc.Sequence):
            raise TypeError('canlist must be like a list')

        # Each rule is a generator yielding bools for the packets sent in
        results = {
            name: rule.test(canlist)
            for name, rule in self.roster.items()
        }

        for _ in canlist:
            yielded = False
            for name, rule in results.items():
                # next() returns next generator item
                if next(rule):
                    yielded = True
                    yield True, name
                    break
            if not yielded:
                yield False, None
