"""Test Rules IDS
Note:
    pytest searches for test_* functions at the module level, or within Test*
    classes.
"""
# pylint: disable=redefined-outer-name

import pytest

import tests.rule_abc_test
from IDS.rules_ids import RulesIDS

TEST_ROSTER = {
    'dummy': tests.rule_abc_test.DummyCl,
    'load': tests.rule_abc_test.LoadCl
}


@pytest.fixture  # default scope is 'function'
def prepared_rules_ids(canlist_good):
    """Create a RulesIDS with prepared rules."""
    rul = RulesIDS('test_preload')
    rul.roster = TEST_ROSTER
    rul.prepare(canlist_good)
    return rul


# look into pytest incremental testing
def test_prepare_save(canlist_good):
    """Test RuleIDS.prepare for accepting data
    Tests:
        - profile ID must be set before prepare() can run.
        - all objects in RuleIDS.roster must be subclasses of Rule
    """
    rul = RulesIDS()

    # test no name
    rul.roster = TEST_ROSTER
    with pytest.raises(ValueError):
        rul.prepare(canlist_good)

    rul.profile_id = 'test'

    # test bad roster
    rul.roster = {'asdf': object}
    with pytest.raises(TypeError):
        rul.prepare(canlist_good)


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


def test_test(prepared_rules_ids, canlist_good):
    single_frame = canlist_good[0]
    # test bad return
    # 'dummy' rule always returns False
    assert prepared_rules_ids.test(single_frame) == (True, 'dummy')
    with pytest.raises(TypeError):
        prepared_rules_ids.test(canlist_good)

    for res in prepared_rules_ids.test_series(canlist_good):
        assert res == (True, 'dummy')

    with pytest.raises(TypeError):
        # test_series is a generator
        next(prepared_rules_ids.test_series(single_frame))

    # test good return
    # remove bad rule
    del prepared_rules_ids.roster['dummy']

    assert prepared_rules_ids.test(single_frame) == (False, None)

    for res in prepared_rules_ids.test_series(canlist_good):
        assert res == (False, None)
