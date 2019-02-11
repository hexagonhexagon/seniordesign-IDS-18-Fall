"""Rule Abstract Base Class"""

import json
import pathlib
from abc import ABC, abstractmethod


class Rule(ABC):
    """Rule Abstract Base Class
    This defines an interface for rules used in the Rules Based IDS.
    Only the “test” function is required to be implemented by a child class.
    If the rule function needs a set of working data for its heuristics,
    then the "prepare" function should be implemented.

    Attributes:
        profile_id: string indicating the usage profile for the rule. For
        example, "Ford_Fusion_2018"

        Working data {multiple, various}: set of information used for an
        algorithm’s operation.  These attributes are to be private, defined by
        each child class as needed. As such, this abstract class will not
        provide declarations for these items.
    """

    # use this file as path reference
    # MAYBE: make a file in project root to define global constants, such as
    # this.
    SAVE_PATH = pathlib.Path(__file__).parent.parent / 'savedata/rule-profiles'

    def __init__(self, profile_id):
        """Init Rule
        Raises:
            ValueError: if profile_id is not a valid python identifier.
        """
        if not profile_id.isidentifier():
            raise ValueError("profile_id needs to be valid python identifier")
        self.profile_id = profile_id
        super().__init__()

    @property
    def save_path(self):
        """Define profile save path"""
        # self.__class__.__name__ provides the name of the current instance.
        # This will be the name of the child class.
        return self.SAVE_PATH / self.profile_id / '{}.json'.format(
            self.__class__.__name__)

    @abstractmethod
    def test(self, canlist):
        """Classify CAN packets
        A function that takes a list of one or more CAN frames, and use a rule
        to classify them. This function will be referenced by the “Test Frame”
        and “Test Series” functions of the Rules IDS class.
        If any working data is needed, it should be defined by implementing the
        "prepare" method.

        Returns: python generator: bool, ...
            The classification is a list of boolean values. The function should
            return one classification for each CAN frame received in the list.
            This list should be returned as a python generator object. bool
            should represent "is_malicious" for a given CAN frame.

        Examples:
            >>> MyRule.test([pak1, pak2, pak3])
            [True, False, True]
        """
        pass

    def prepare(self, canlist=None):
        """Prepare rule heuristics
        This method should be implemented as needed.

        Analyze a list of CAN packets to provide working data for the test
        method.
        If CAN data is not provided, existing working data should be loaded
        from save files. The _load method can be used for this.

        Working data should be saved to a JSON file named after the class
        writing it (e.g. 'Whitelist.json' for class 'Whitelist'). The file
        should be placed in a subfolder of the “savedata” directory,
        corresponding to the vehicle profile (e.g. Ford_Fusion_2018).
        The Rule abstract class "save_path" property is provided to establish
        this.
        The JSON should be a dictionary, with each key corresponding to the
        class attribute name of the data being saved. For example:
        {'whitelist': self.whitelist}.

        Args:
            canlist: default = None
            A list of CAN packets to analyze. If this argument is present, this
            function should analyze the data accordingly and save it,
            overwriting any existing data for that profile.
            Else, the function should attempt to load saved profile data.
        Raises:
            FileNotFoundError: If data required, but not found. If data
            not required, this method should not be implemented.
        """
        pass

    def _load(self):
        """Load saved profile state
        This method loads data from a JSON file previously stored by
        Rule.prepare
        Note that the data contained in the JSON file will be unpacked into
        attributes for this instance of Rule, to be used by the 'test' method
        implemented by the child class.
        Notes:
            This allows for execution of arbitrary code
            This method is marked as private, because it is intented to only be
            used by child classes.
        
        Raises:
            FileNotFoundError
        """
        with self.save_path.open() as prof:
            attr_dict = json.load(prof)
        # unpack loaded JSON into class instance
        for name, val in attr_dict.items():
            setattr(self, name, val)

    def _save(self, savedata):
        """Helper function to save class data, and automatically create parent
        directories if not existant.
        Args:
            savedata: dictionary representing class attributes to save.
                Should be of the form {attr_name: data}
        Note:
            JSON can only save certain base file types, such as dicts or lists.
            Other types would need a custom encoder function.
        """

        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        with self.save_path.open('w') as prof:
            json.dump(savedata, prof)
