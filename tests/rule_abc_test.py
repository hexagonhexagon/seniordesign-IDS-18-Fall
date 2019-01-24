"""Rule Abstract Base Class Testing

Note:
    pytest searches for test_* functions at the module level, or within Test*
    classes.
    So, in this file, classes inheriting from Rule, can't have a name of Test*

    At least when running pytest, relative paths start in pytest's working
    directory. using pathlib helps avoid this confusion
"""
# pylint: disable=redefined-outer-name

import pathlib
import pytest

from IDS.rule_abc import Rule

SAMPLE = [{
    'id': 530,
    'timestamp': 14827347905780,
    'data': b'\xc0\x14\xe1D\x02\x00\x14\xf0'
}, {
    'id': 577,
    'timestamp': 14827347905780,
    'data': b'\x1c/\x1e/p\x17p\x17'
}]

#--------------------#
#  Test Basic Usage  #
#--------------------#


class DummyCl(Rule):
    """Dummy rule for testing minimal usage of the class"""

    def test(self, canlist):
        for pak in canlist:
            yield pak['id'] != pak['id']


def test_dummy():
    # profile_id must be a valid python identifier
    with pytest.raises(ValueError):
        dum = DummyCl('FSD&)*( ')

    dum = DummyCl('test_dummy')
    # check that prepare() can be called despite not being implemented by the
    # child
    dum.prepare()
    assert not any(dum.test(SAMPLE))


#---------------------#
#  Test Data Loading  #
#---------------------#


class LoadCl(Rule):
    """Test Rule._load()
    Can't define as a Test* class, since Rule requires a test() method.
    """

    def test(self, canlist):
        for asdf_id, can_id in zip(self.asdf, (x['id'] for x in canlist)):
            yield asdf_id == can_id

    def prepare(self, canlist=None):
        if canlist:
            self.asdf = [x['id'] for x in canlist]
            savedata = {'asdf': self.asdf}
            super()._save(savedata)
        else:
            super()._load()


def test_load():
    """Test Rule._load()"""
    sample_path = pathlib.Path(__file__).parent.parent / \
        'savedata/rule-profiles/test_load/LoadCl.json'
    # delete any existing file
    try:
        sample_path.unlink()
    except FileNotFoundError:
        pass

    asdf = LoadCl('test_load')
    with pytest.raises(FileNotFoundError):
        asdf.prepare()

    asdf.prepare(SAMPLE)
    # check that save file was created correctly
    assert sample_path.is_file()

    # load savedata
    asdf = LoadCl('test_load')
    asdf.prepare()
    assert all(asdf.test(SAMPLE))
    # remove sample file (check out pytest fixtures for this)
    sample_path.unlink()
    sample_path.parent.rmdir()
