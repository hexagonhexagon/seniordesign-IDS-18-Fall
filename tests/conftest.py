"""Pytest local plugin module
Adds configurations and definitions to be used by pytest, for the
folder/package that this is in.
"""
# pylint: disable = redefined-outer-name

import pathlib

import pytest

import IDS.malicious
import IDS.preprocessor

TEST_DIR = pathlib.Path(__file__).parent


@pytest.fixture(scope='module')
def canlist_good():
    """Get Sample CAN Data for testing"""
    small_sample = IDS.preprocessor.parse_traffic(
        TEST_DIR / 'sample_data/traffic/asia_train.traffic')
    return small_sample


@pytest.fixture
def malgen():
    """Provides an initialized MaliciousGenerator object"""
    new_malgen = IDS.malicious.MaliciousGenerator()
    # update probabilities for testing
    new_malgen.adjust({'none': 0.8})
    return new_malgen


@pytest.fixture
def canlist_bad(canlist_good, malgen):
    """Insert malicious packets randomly into canlist_good"""
    badlist, labels = IDS.preprocessor.inject_malicious_packets(
        canlist_good, malgen)
    # labels returned by inject_malicious_packets are ints (0,1) for
    # "is malicious", but rules return bools for "passed rule"
    answers = [not bool(x) for x in labels]
    return badlist, answers
