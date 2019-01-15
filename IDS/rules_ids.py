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

import rules
import rule_abc


class RulesIDS:
    """Examine CAN packets according to a set of rules."""

    def __init__(self, profile_id=None):
        """Init IDS
        If profile is specified now, prepare will be run, else it will have to
        be called separately
        """
        self.profile_id = profile_id
        self.roster = rules.ROSTER

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
        for name, item in self.roster.items():
            if not issubclass(item, rule_abc.Rule):  # Necessary?
                raise ValueError("{}: {} is not a Rule.".format(
                    name, type(item)))
            rule_instance = item(self.profile_id)
            rule_instance.prepare(canlist)
            new_roster[name] = rule_instance
        self.roster = new_roster

    def test(self, can_frame):
        """Examine single CAN packet according to rules in the roster
        Args:
            can_frame: a single CAN packet

        Returns:
            Tuple (bool, str)
            Returns on the first rule to fail, with str as the name of the rule
            that failed the packet. Else, str is None
        """
        for name, rule in self.roster.items():
            # Each rule returns a boolean list for the packets sent in
            result = rule.test([can_frame])
            if not result[0]:
                return False, name
        return True, None

    def test_series(self, canlist):
        """Examine list of CAN packets according to rules in the roster
        Args:
            canlist: a list of CAN packets

        Returns:
            List of tuples (bool, str), corresponding to packets in input list
            str is the name of the rule to first fail a given packet, or None
            if passed.
        """

        results = []
        for name, rule in self.roster.items():
            # Each rule returns a boolean list for the packets sent in
            for ii, val in enumerate(rule.test(canlist)):
                if ii >= len(results):
                    if val:
                        results.append((val, None))
                    else:
                        results.append((val, name))
                else:
                    # if first fail
                    if not val and results[ii][0]:
                        results[ii] = (val, name)

        return results
