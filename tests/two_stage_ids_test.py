from IDS.two_stage_ids import TwoStageIDS
from IDS.dnn_ids import dnn_input_function
import IDS.preprocessor as dp
import os.path

import pytest

test_dir = os.path.dirname(__file__)

@pytest.fixture
def feature_lists_labels():
    return dp.load_feature_lists(test_dir + '/sample_data/two_stage_ids_test/features.json')

@pytest.fixture
def bad_canlist():
    return dp.load_canlist(test_dir + '/sample_data/two_stage_ids_test/badlist.json')

@pytest.fixture
def prepared_ids(canlist_good, feature_lists_labels):
    features, labels = feature_lists_labels
    ids = TwoStageIDS()
    ids.change_ids_parameters('dnn_dir_path', test_dir + '/../savedata/test_dnn')
    ids.change_ids_parameters('rules_profile', 'test_rules')
    ids.change_ids_parameters('idprobs_path', test_dir + '/sample_data/two_stage_ids_test/idprobs.json')
    ids.init_ids()
    if not ids.rules_trained:
        ids.retrain_rules(canlist_good)
    if not ids.dnn_trained:
        ids.train_dnn(dnn_input_function(features, labels, shuffle=True), 2000)
    return ids


def test_change_parameters(prepared_ids: TwoStageIDS):
    # Check that invalid keys raise a ValueError for change_ids_parameters.
    with pytest.raises(ValueError):
        prepared_ids.change_ids_parameters('invalid_key', 'invalid_value')

    # Check that changing parameters works correctly.
    ids = prepared_ids
    ids.change_ids_parameters('dnn_dir_path', 'test')
    ids.change_ids_parameters('rules_profile', 'test')
    ids.change_ids_parameters('idprobs_path', 'test')
    assert ids.params == {
        'dnn_dir_path': 'test',
        'rules_profile': 'test',
        'idprobs_path': 'test'
    }

    # Check that initialized DNN can't have parameters changed.
    with pytest.raises(RuntimeError):
        ids.change_dnn_parameters('hidden_units', 'test')

    # Check that invalid keys raise a ValueError for change_dnn_parameters.
    ids = TwoStageIDS()
    with pytest.raises(ValueError):
        ids.change_dnn_parameters('invalid_key', 'invalid_value')

    # Check that changing parameters works correctly.
    ids.change_dnn_parameters('hidden_units', 'test')
    ids.change_dnn_parameters('optimizer', 'test')
    ids.change_dnn_parameters('activation_fn', 'test')
    ids.change_dnn_parameters('loss_reduction', 'test')
    assert ids.dnn._params == {
        'hidden_units': 'test',
        'optimizer': 'test',
        'activation_fn': 'test',
        'loss_reduction': 'test'
    }

def test_init_ids(prepared_ids: TwoStageIDS):
    # Check that loading existing trained model works properly.
    ids = prepared_ids
    assert ids.rules_trained
    assert ids.rules.profile_id == 'test_rules'
    assert ids.dnn_trained
    assert ids.dnn._dnn

    ids.change_ids_parameters('dnn_dir_path', test_dir + '/../savedata/test_dnn_2')
    ids.change_ids_parameters('rules_profile', 'test_rules_2')
    # First round: test creation of new model
    # Second round: test loading of old model
    try:
        for _ in range(2):
            ids.init_ids()
            assert not ids.rules_trained
            assert not ids.dnn_trained
    finally:
        # Remove any files that were created during the testing.
        # Will run even if exception is raised.
        os.remove(test_dir + '/../savedata/test_dnn_2.params')

    # Check that having an invalid idprobs_path causes an error.
    ids.change_ids_parameters('idprobs_path', 'does_not_exist')
    with pytest.raises(FileNotFoundError):
        ids.init_ids()

def test_training(prepared_ids: TwoStageIDS, feature_lists_labels, canlist_good):
    # Check that retraining rules works properly.
    prepared_ids.retrain_rules(canlist_good)
    assert prepared_ids.rules_trained

    # Check that training the DNN works properly.
    features, labels = feature_lists_labels
    prepared_ids.train_dnn(dnn_input_function(features, labels, shuffle=True), 2000)
    assert prepared_ids.dnn_trained

    # Check that trying to train the DNN without an initialized DNN Based IDS
    # causes an error.
    not_initialized_ids = TwoStageIDS()
    with pytest.raises(RuntimeError):
        not_initialized_ids.train_dnn(dnn_input_function(features, labels, shuffle=True), 2000)

def test_judge_dataset(prepared_ids: TwoStageIDS, feature_lists_labels, bad_canlist):
    features, labels = feature_lists_labels
    ids = TwoStageIDS()
    # Test trying to judge dataset when DNN isn't trained.
    with pytest.raises(RuntimeError, match='The DNN must be trained'):
        ids.judge_dataset(bad_canlist, dnn_input_function(features, labels))
    ids.dnn_trained = True
    # Test trying to judge dataset when Rules IDS isn't trained.
    with pytest.raises(RuntimeError, match='The Rules Based IDS must be prepared'):
        ids.judge_dataset(bad_canlist, dnn_input_function(features, labels))

    ids = prepared_ids
    ids.start_simulation()
    # Test trying to judge dataset while in simulation.
    with pytest.raises(RuntimeError, match='The TwoStageIDS must not be in a simulation'):
        ids.judge_dataset(bad_canlist, dnn_input_function(features, labels))
    ids.stop_simulation()

    # Verify that judging dataset produces a good output.
    results = ids.judge_dataset(bad_canlist, dnn_input_function(features, labels))
    for result in results:
        assert isinstance(result, tuple) and isinstance(result[0], bool) and (isinstance(result[1], float) or isinstance(result[1], str))

def test_simulation(prepared_ids: TwoStageIDS, bad_canlist):
    single_frame = bad_canlist[0]
    ids = prepared_ids
    # Test that trying to judge a single frame does not work outside of a
    # simulation.
    with pytest.raises(RuntimeError, match='not currently in a simulation'):
        ids.judge_single_frame(single_frame)

    ids.start_simulation()
    # Verify that judge single frame produces a good output.
    for frame in bad_canlist[:100]:
        result = ids.judge_single_frame(frame)
        assert isinstance(result, tuple) and isinstance(result[0], bool) and (isinstance(result[1], float) or isinstance(result[1], str))
    ids.stop_simulation()