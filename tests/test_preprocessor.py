"""Testing for IDS Data Preprocessor"""

import io
import pathlib
import sys
from ast import literal_eval

import pytest

import IDS.preprocessor as dp
from IDS.malicious import MaliciousGenerator

SAMPLE_PATH = pathlib.Path(__file__).parent / 'sample_data'


def test_parse_traffic():
    # Check parse_traffic
    frames = dp.parse_traffic(SAMPLE_PATH / 'traffic/asia_train.traffic')
    with open(str(SAMPLE_PATH / 'test_preprocessor/traffic_validate.txt')) \
            as verification_file:
        frames_check = literal_eval(verification_file.read())
    assert frames == frames_check

    frames = dp.parse_traffic(
        str(SAMPLE_PATH / 'traffic/local_Aug_31_trimmed.traffic'))
    with open(SAMPLE_PATH / 'test_preprocessor/traffic_validate_2.txt') \
            as verification_file:
        frames_check = literal_eval(verification_file.read())
    assert frames == frames_check

    with pytest.raises(FileNotFoundError):
        dp.parse_traffic('asdf')

    with pytest.raises(FileNotFoundError):
        dp.parse_traffic('.')

    with pytest.raises(ValueError):
        dp.parse_traffic(str(SAMPLE_PATH.parent / 'test_preprocessor.py'))


def test_parse_csv():
    # Check parse_csv
    frames = dp.parse_csv(
        str(SAMPLE_PATH /
            'csv/2006 Ford Fusion/Test Data/2006 Ford Fusion Test.csv'))
    with open(SAMPLE_PATH / 'test_preprocessor/csv_validate.txt') \
            as verification_file:
        frames_check = literal_eval(verification_file.read())
    assert frames == frames_check

    with pytest.raises(FileNotFoundError):
        dp.parse_csv('asdf')

    with pytest.raises(FileNotFoundError):
        dp.parse_csv('.')

    with pytest.raises(ValueError):
        dp.parse_csv(str(SAMPLE_PATH.parent / 'test_preprocessor.py'))


def test_validate_can_data():
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO(
    )  # Write anything being printed to stdout to buffer instead

    frames = dp.parse_csv(
        str(SAMPLE_PATH /
            'csv/2006 Ford Fusion/Test Data/2006 Ford Fusion Test.csv'))
    assert dp.validate_can_data(frames)
    frames[163].pop('id')
    frames[124]['id'] = 3999
    frames[777]['timestamp'] = 'asdf'
    frames[32]['data'] = b'aaaaaaaaaaaa'
    frames[32]['timestamp'] = -1
    frames[777]['data'] = 3.1
    assert not dp.validate_can_data(frames)

    # Check that what was being printed is the correct output
    sys.stdout = old_stdout
    assert buffer.getvalue() == """This dataset is valid!
Frame index 32's timestamp is negative: actually -1!
Frame index 32's data field is longer than 8 bytes: actually 12 bytes long!
Frame index 124's ID is outside the range 0-2047: actually 3999!
Frame index 163 does not have the key 'id'!
Frame index 777's timestamp is not an integer: actually a <class 'str'>, value 'asdf'!
Frame index 777's data is not a bytes object: actually a <class 'str'>, value 'asdf'!
This dataset is invalid!\n"""


def test_id_probs(tmp_path):
    frames = dp.parse_csv(
        SAMPLE_PATH /
        'csv/2006 Ford Fusion/Test Data/2006 Ford Fusion Test.csv')
    probs_file = str(tmp_path / 'idprobs.json')
    dp.write_id_probs(frames, probs_file)
    idprobs = dp.load_id_probs(probs_file)
    idprobs_check = {
        1072: 0.07521674607513865,
        336: 0.15019917206904632,
        352: 0.15019917206904632,
        560: 0.15019917206904632,
        71: 0.015621338748730767,
        357: 0.0937280324923846,
        368: 0.0937280324923846,
        512: 0.0937280324923846,
        513: 0.0937280324923846,
        1056: 0.015621338748730767,
        1058: 0.015621338748730767,
        65: 0.014996485198781535,
        832: 0.014996485198781535,
        848: 0.014996485198781535,
        613: 0.0014840271811294228,
        1279: 0.0014840271811294228,
        1108: 0.0014840271811294228,
        1059: 0.0014840271811294228,
        1107: 0.0014840271811294228
    }
    assert idprobs == idprobs_check


def test_feature_lists(tmp_path):
    frames = dp.parse_csv(
        SAMPLE_PATH /
        'csv/2006 Ford Fusion/Test Data/2006 Ford Fusion Test.csv')
    idprobs = dp.write_id_probs(frames, tmp_path / 'idprobs')

    feature_lists = dp.generate_feature_lists(frames, idprobs)
    feat_file = tmp_path / 'feature_lists'
    dp.write_feature_lists(feature_lists, [], feat_file)
    feature_lists, _ = dp.load_feature_lists(feat_file)
    with open(SAMPLE_PATH / 'test_preprocessor/feature_lists_validate.txt') \
            as validation_file:
        feature_lists_check = literal_eval(validation_file.read())
    assert feature_lists == feature_lists_check


def test_inject_malicious_packets():
    frames = dp.parse_csv(
        SAMPLE_PATH /
        'csv/2006 Ford Fusion/Test Data/2006 Ford Fusion Test.csv')
    prev_len = len(frames)
    mg = MaliciousGenerator()
    frames, labels = dp.inject_malicious_packets(frames, mg)
    assert len(frames) == len(labels)
    assert 1 in labels
    assert len(frames) > prev_len
    assert dp.validate_can_data(frames)
