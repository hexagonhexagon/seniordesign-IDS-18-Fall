"""Testing Rules Library"""
# Note:
#     pytest searches for test_* functions at the module level, or within Test*
#     classes.

# pylint: disable = redefined-outer-name

# TODO: it would probably be better to try to test 'test' and 'prepare'
# separately, for each rule.

import collections

import pytest

import ids.rules

# False positive/negative rates to be considered passing.
# values are probabilities [0, 1], and compared inclusively ( <= )
ALLOWED_FALSE_POSITIVES = 0.1
ALLOWED_FALSE_NEGATIVES = 0.4


@pytest.fixture
def canlist_bad_whitelist(canlist_good, canlist_bad):
    """Modify default canlist_bad for test_whitelist
    This is to remove possibility of false-negatives/positives
    """
    goodlist = set(x['id'] for x in canlist_good)
    new_badlist = []
    new_answers = []
    for pak, bad in zip(*canlist_bad):
        if (pak['id'] in goodlist and not bad) \
                or (pak['id'] not in goodlist and bad):
            new_badlist.append(pak)
            new_answers.append(bad)
    return new_badlist, new_answers


def check_rule(rul, can_ans):
    """check rule output
    perform check by calculating false-negative and false-positive rates.
    """
    badlist, answers = can_ans
    false_counts = collections.Counter()  # defaults any key to 0
    results = rul.test(badlist)
    # result and answer represent "is_malicious" for a given CAN packet
    for result, answer in zip(results, answers):
        if result != answer:
            if answer:  # bad packet; passed rule
                false_counts['negative'] += 1
            else:  # good packet; failed rule
                false_counts['positive'] += 1

    print('false-positives: {} / {}'.format(false_counts['positive'],
                                            len(badlist)))
    print('false-negatives: {} / {}'.format(false_counts['negative'],
                                            len(badlist)))
    assert false_counts['positive'] / len(badlist) <= ALLOWED_FALSE_POSITIVES
    assert false_counts['negative'] / len(badlist) <= ALLOWED_FALSE_NEGATIVES


def test_whitelist(canlist_good, canlist_bad_whitelist, tmp_path):
    """Testing ID_Whitelist rule"""

    def empty_rule():
        rul = ids.rules.ID_Whitelist('test')
        rul.SAVE_PATH = tmp_path
        return rul

    rul = empty_rule()
    rul.prepare(canlist_good)
    check_rule(rul, canlist_bad_whitelist)

    # check data loading
    rul = empty_rule()
    rul.prepare()
    check_rule(rul, canlist_bad_whitelist)


def test_timeinterval(canlist_good, canlist_bad, tmp_path):
    """Testing TimeInterval rule"""

    def empty_rule():
        rul = ids.rules.TimeInterval('test')
        rul.SAVE_PATH = tmp_path
        return rul

    rul = empty_rule()
    rul.prepare(canlist_good)
    presave = [rul.bins, rul.valid_bins]
    check_rule(rul, canlist_bad)

    # check data loading
    rul = empty_rule()
    rul.prepare()
    postsave = [rul.bins, rul.valid_bins]
    check_rule(rul, canlist_bad)

    # check save & load is correct
    assert presave == postsave


def test_frequency(canlist_good, canlist_bad, tmp_path):
    """Testing MessageFrequency rule"""

    def empty_rule():
        rul = ids.rules.MessageFrequency('test')
        rul.SAVE_PATH = tmp_path
        return rul

    rul = empty_rule()
    rul.prepare(canlist_good)
    presave = rul.frequencies
    check_rule(rul, canlist_bad)

    # check data loading
    rul = empty_rule()
    rul.prepare()
    postsave = rul.frequencies
    check_rule(rul, canlist_bad)

    # check save & load is correct
    assert presave == postsave


def test_sequence(canlist_good, canlist_bad, tmp_path):
    """Testing MessageSequence rule"""

    def empty_rule():
        rul = ids.rules.MessageSequence('test')
        rul.SAVE_PATH = tmp_path
        return rul

    rul = empty_rule()
    rul.prepare(canlist_good)
    presave = rul.sequences
    check_rule(rul, canlist_bad)

    # check data loading
    rul = empty_rule()
    rul.prepare()
    postsave = rul.sequences
    check_rule(rul, canlist_bad)

    # check save & load is correct
    assert presave == postsave
