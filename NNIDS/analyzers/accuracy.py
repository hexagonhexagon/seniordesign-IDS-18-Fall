class AccuracyAnalyzer:
    """ Class for analyzing classifier accuracy """

    def __init__(self, message_types, correct_labels, classifier_predictions):
        """
        Initialize AccuracyAnalyzer object

        :param message_types: list of message types in order of receipt
        :param correct_labels: list of message labels in order of receipt
        :param classifier_predictions: list of predictions in order of receipt
        """

        self.msg_types = message_types
        self.labels = correct_labels
        self.predictions = classifier_predictions

        self.num_correct = 0
        self.num_malicious = 0
        self.num_caught = 0
        self.num_false_positives = 0
        self.num_classified_malicious = 0

        self.num_valid = 0
        self.num_injected = 0
        self.num_spoof = 0
        self.num_dos = 0

        self.num_valid_caught = 0
        self.num_injected_caught = 0
        self.num_spoof_caught = 0
        self.num_dos_caught = 0

        for i in range(0, len(self.predictions)):
            if int(self.predictions[i][0]) == self.labels[i]:
                self.num_correct += 1
            if self.labels[i] == 1:
                self.num_malicious += 1
                if int(self.predictions[i][0]) == 1:
                    self.num_caught += 1
            if int(self.predictions[i][0]) == 1:
                self.num_classified_malicious += 1
                if self.labels[i] == 0:
                    self.num_false_positives += 1
            if self.msg_types[i] == 'Valid':
                self.num_valid += 1
                if int(self.predictions[i][0]) == 0:
                    self.num_valid_caught += 1
            elif self.msg_types[i] == 'Random injection':
                self.num_injected += 1
                if int(self.predictions[i][0]) == 1:
                    self.num_injected_caught += 1
            elif self.msg_types[i] == 'Spoofing':
                self.num_spoof += 1
                if int(self.predictions[i][0]) == 1:
                    self.num_spoof_caught += 1
            elif self.msg_types[i] == 'DOS':
                self.num_dos += 1
                if int(self.predictions[i][0]) == 1:
                    self.num_dos_caught += 1

    def print_accuracy_statistics(self):
        """
        Print statistics for accuracy data

        :return: None
        :raises ValueError:
            if any of self.labels, self.predictions, and self.msg_types is empty
            if the length of self.labels, self.predictions, and self.msg_types differ
        """
        if len(self.labels) == 0:
            raise ValueError('AccuracyAnalyzer object has no label data')
        if len(self.predictions) == 0:
            raise ValueError('AccuracyAnalyzer object has no predictions data')
        if len(self.msg_types) == 0:
            raise ValueError('AccuracyAnalyzer object has no msg_types data')

        if len(self.labels) != len(self.predictions):
            raise ValueError('The number of labels and predictions differ')
        if len(self.labels) != len(self.msg_types):
            raise ValueError('The number of labels and msg_types differ')
        if len(self.predictions) != len(self.msg_types):
            raise ValueError('The number of predictions and msg_types differ')

        print('\nACCURACY STATISTICS')
        print('Percentage correct:\n\t' + str(self.num_correct)
              + ' correct / ' + str(len(self.labels)) + ' total = '
              + str(self.num_correct / len(self.labels) * 100) + '%')
        if self.num_malicious != 0:
            print('Percentage of malicious messages caught:\n\t' + str(self.num_caught)
                  + ' correct / ' + str(self.num_malicious) + ' total = '
                  + str(self.num_caught / self.num_malicious * 100) + '%')
        else:
            print('No malicious messages received')

        if self.num_classified_malicious != 0:
            print('Percentage of false positives:\n\t' + str(self.num_false_positives)
                  + ' incorrect / ' + str(self.num_classified_malicious) + ' total = '
                  + str(float(self.num_false_positives) / float(self.num_classified_malicious)
                        * 100) + '%')
        else:
            print('No messages classified as malicious')

        print()
        print('Valid message statistics: ' + str(self.num_valid_caught) + ' correct / '
              + str(self.num_valid) + ' total = '
              + str(self.num_valid_caught / float(self.num_valid)))

        if self.num_injected != 0:
            print('Random injection statistics: ' + str(self.num_injected_caught) + ' caught / '
                  + str(self.num_injected) + ' total = '
                  + str(self.num_injected_caught / float(self.num_injected)))
        else:
            print('No messages randomly injected')

        if self.num_spoof != 0:
            print('Spoofing statistics: ' + str(self.num_spoof_caught) + ' caught / '
                  + str(self.num_spoof) + ' total = '
                  + str(self.num_spoof_caught / float(self.num_spoof)))
        else:
            print('No spoofing messages injected')

        if self.num_dos != 0:
            print('DOS statistics: ' + str(self.num_dos_caught) + ' caught / ' + str(self.num_dos)
                  + ' total = ' + str(self.num_dos_caught / float(self.num_dos)))
        else:
            print('No DOS messages injected')

        print()
        print('Number of malicious messages: ' + str(self.num_malicious))
        print('Number of messages: ' + str(len(self.labels)))
