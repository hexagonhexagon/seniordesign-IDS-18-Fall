"""Rule Abstract Base Class"""

from abc import ABC, abstractmethod

class Rule(ABC):
    """Rule Abstract Base Class
    This is an abstract class; it defines an interface for child classes to
    implement. Each rule for use in the Rules Based IDS should derive from this
    class. Only the “Test” function is required to be implemented by a child
    class. If the rule function needs a set of working data for its heuristics,
    then the "Prepare" function should be implemented.

    Attributes:
        profile_id: string indicating the usage profile for the rule. For
        example, "Ford_Fusion_2018"

        Working data {multiple, various}: set of information used for an
        algorithm’s operation.  These properties are to be private, defined by
        each child class as needed. As such, this abstract class will not
        provide declarations for these items.
    """

    def __init__(self, profile_id):
        # Define attributes all rules should have
        self.profile_id = profile_id
        # Initialize super-class
        super().__init__()
        self.prepare()

    @abstractmethod
    def test(self, canlist):
        """Classify CAN packets
        A function that takes a list of one or more CAN frames, and use a rule
        to classify them. This function will be referenced
        by the “Test Frame” and “Test Series” functions of the Rules IDS
        class.

        Returns: [ bool, ... ]
            The classification is a list of boolean values. The function should
            return one classification for each CAN frame received in the list.

        Examples:
            >>> MyRule.test([pak1, pak2, pak3])
            [True, False, True]
        """
        pass

    def prepare(self, canlist=None):
        """
        This method should be implemented as needed.
        Accepts a list of CAN frames and a string identifier for the vehicle
        profile. Analyze a list of CAN packets to provide working data for a
        corresponding Rule Function. 
        Working data should be saved to a JSON file named after the class
        writing it (e.g. Whitelist.json), in a subfolder of the “savedata”
        directory, corresponding to the vehicle profile (e.g. Ford_Fusion_2018)
        that is being prepared. If the working data already exists for that
        profile, it will be loaded.

        Args:
            canlist: default = None
            A list of CAN packets to analyze. If this argument is present, this
            function should analyze the data accordingly and save it,
            overwriting any existing data for that profile.
            Else, the function should check for saved profile data.
        Raises:
            If data required, but not found, raise a FileNotFoundError. If data
            not required, this method should not be implemented.

        """
        pass

