import numpy as np
import time


class OperationAnalyzer:
    """ Class for analyzing runtime and memory """
    def __init__(self):
        """
        Initialize OperationAnalyzer object. Set self.runtimes to empty dict.
        """
        self.runtimes = {}

    def add_runtime(self, start_time, stop_time, operation_type):
        """
        Adds a runtime data point to self.runtimes.

        :param start_time: start time of operation
        :param stop_time: end time of operation
        :param operation_type: type of operation, allows sorting of runtime statistics by category
        :return: None
        :raises ValueError: if stop_time occurs before start_time
        """
        if start_time - stop_time > 0.00001:
            raise ValueError('stop_time occurs before start_time')

        if operation_type not in self.runtimes:
            self.runtimes[operation_type] = np.array([])
        self.runtimes[operation_type] = np.append(self.runtimes[operation_type],
                                                  stop_time - start_time)

    @property
    def max_runtime(self, operation_type=None):
        """
        Return the maximum runtime logged in all categories if operation_type is None,
        else return the maximum runtime logged in the category operation_type

        :param operation_type: select the category to analyze
        :return: the maximum runtime
        """
        if operation_type is None:
            temp_array = np.array([])
            for key in self.runtimes:
                temp_array = np.append(temp_array, self.runtimes[key])
            return np.max(temp_array)
        return np.max(self.runtimes[operation_type])

    @property
    def average_runtime(self, operation_type=None):
        """
        Return the average runtime logged in all categories if operation_type is None,
        else return the average runtime logged in the category operation_type

        :param operation_type: select the category to analyze
        :return: the average runtime
        """
        if operation_type is None:
            temp_array = np.array([])
            for key in self.runtimes:
                temp_array = np.append(temp_array, self.runtimes[key])
            return np.average(temp_array)
        return np.average(self.runtimes[operation_type])

    @property
    def median_runtime(self, operation_type=None):
        """
        Return the median runtime logged in all categories if operation_type is None,
        else return the median runtime logged in the category operation_type

        :param operation_type: select the category to analyze
        :return: the median runtime
        """
        if operation_type is None:
            temp_array = np.array([])
            for key in self.runtimes:
                temp_array = np.append(temp_array, self.runtimes[key])
            return np.median(temp_array)
        return np.median(self.runtimes[operation_type])

    def print_runtime_statistics(self, units):
        """
        Print statistics for runtime data

        :param units: str, name of units to be displayed in messages
        :return: None
        """

        print('\nRUNTIME STATISTICS')

        temp_array = np.array([])
        for key in self.runtimes:
            temp_array = np.append(temp_array, self.runtimes[key])

        print('Overall maximum runtime: ' + str(np.max(temp_array)) + ' ' + units)
        print('Overall average runtime: ' + str(np.average(temp_array)) + ' ' + units)
        print('Overall median runtime: ' + str(np.median(temp_array)) + ' ' + units)

        for key in sorted(self.runtimes.keys()):
            print('\nRuntime Statistics for ' + str(key))
            print('\tMaximum runtime: ' + str(np.max(self.runtimes[key])) + ' ' + units)
            print('\tAverage runtime: ' + str(np.average(self.runtimes[key])) + ' ' + units)
            print('\tMedian runtime: ' + str(np.median(self.runtimes[key])) + ' ' + units)
