"""Rule Abstract Base Class Testing

Note:
    pytest searches for test_* functions at the module level, or within Test*
    classes.
    So, in this file, classes inheriting from Rule, can't have a name of Test*
"""

import json
import os

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
        for _ in canlist:
            yield False


def test_dummy():
    dum = DummyCl('test_dummy')
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
            with self.save_file.open('w') as prof:
                savedata = {'asdf': [x['id'] for x in canlist]}
                json.dump(savedata, prof)
        else:
            super()._load()


def test_load():
    """Test Rule._load()"""
    asdf = LoadCl('test_load')
    asdf.prepare(SAMPLE)
    # check that save file was created correctly
    assert os.path.isfile('../savedata/test_load/LoadCl.json')

    # load savedata
    asdf.prepare()
    assert all(asdf.test(SAMPLE))

