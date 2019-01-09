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

def prepare():
    """Prepare rule heuristics with working data
    Some rules require whitelists or other such data for their operation.
    """
    # TODO: where does this data come from?
    pass

def test(can_frame):
    """Examine single CAN packet according to rules in the roster
    Args:
        can_frame: a single or list of CAN packets

    Returns:
        Boolean value
    """
    results = []
    for rule in rules.ROSTER.values():
        # Each rule returns a boolean list for the packets sent in
        results.append(rule([can_frame]))

    return sum(x[0] for x in results) == len(results)

def test_series(canlist):
    """Examine list of CAN packets according to rules in the roster
    Args:
        canlist: a single or list of CAN packets

    Returns:
        List of boolean values, corresponding to packets in input list
    """

    results = []
    for rule in rules.ROSTER.values():
        # Each rule returns a boolean list for the packets sent in
        if not results:
            results = rule(canlist)
        else:
            # combine boolean lists
            results = [x and y for x, y in zip(results, rule(canlist))]

    return results
