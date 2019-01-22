"""Test Rules IDS
Note:
    pytest searches for test_* functions at the module level, or within Test*
    classes.
"""

import pytest

import tests.rule_abc_test
from IDS.rule_abc import Rule
from IDS.rules_ids import RulesIDS

TEST_ROSTER = {
    'dummy': tests.rule_abc_test.DummyCl,
    'load': tests.rule_abc_test.LoadCl
}


@pytest.fixture(scope='module')
def sample_canlist():
    """Get Sample CAN Data for testing
    As it is, there's no point making this a fixture.
    """
    # for now just use the 2 packets in rule_abc_test
    return tests.rule_abc_test.SAMPLE


@pytest.fixture  # default scope is 'function'
def prepared_rules_ids(sample_canlist):
    """Create a RulesIDS with prepared rules."""
    rul = RulesIDS('test_preload')
    rul.roster = TEST_ROSTER
    rul.prepare(sample_canlist)
    return rul


# look into pytest incremental testing
def test_prepare_save(sample_canlist):
    """Test RuleIDS.prepare for accepting data
    Tests:
        - profile ID must be set before prepare() can run.
        - all objects in RuleIDS.roster must be subclasses of Rule
    """
    rul = RulesIDS()

    # test no name
    rul.roster = TEST_ROSTER
    try:
        rul.prepare(sample_canlist)
    except ValueError:
        pass
    else:
        assert False
    rul.profile_id = 'test'

    # test bad roster
    rul.roster = {'asdf': object}
    try:
        rul.prepare(sample_canlist)
    except ValueError:
        pass
    else:
        assert False


# NOTE: vague test; maybe useless?
# I guess it just tests that prepare() can be called without providing data
def test_prepare_load(prepared_rules_ids):
    """Test RuleIDS.prepare for loading saved profile data"""
    # prepared_rules_ids will have already saved the profile data.
    rul = RulesIDS()
    rul.profile_id = prepared_rules_ids.profile_id
    rul.roster = TEST_ROSTER
    rul.prepare()
    # Can't know if any rules have working data or not.


def test_test(prepared_rules_ids, sample_canlist):
    single_frame = sample_canlist[0]
    # test bad return
    # 'dummy' rule always returns False
    assert prepared_rules_ids.test(single_frame) == (False, 'dummy')
    try:
        prepared_rules_ids.test(sample_canlist)
    except TypeError:  # TODO: which one?
        pass
    else:
        assert False

    for res in prepared_rules_ids.test_series(sample_canlist):
        assert res == (False, 'dummy')

    try:
        # test_series is a generator
        next(prepared_rules_ids.test_series(single_frame))
    except TypeError:  # TODO: which one?
        pass
    else:
        assert False

    # test good return
    # remove bad rule
    del prepared_rules_ids.roster['dummy']
    print(prepared_rules_ids.roster['load'])
    assert prepared_rules_ids.test(single_frame) == (True, None)
    for res in prepared_rules_ids.test_series(sample_canlist):
        assert res == (True, None)
