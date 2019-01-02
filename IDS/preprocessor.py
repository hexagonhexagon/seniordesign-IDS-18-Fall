import csv
import json
import re
import struct
import os.path
import numpy as np

class DataPreprocessor:
    """A class that handles preprocessing raw CAN message data and converting it to feature sets.

    Functions:
    parse_traffic -- Take in the path to a .traffic file, parse the file, and return a list of CAN messages.
    parse_csv -- Take in the path to a CAN frame .csv file, parse the file, and return a list of CAN messages.
    validate_can_data -- Take in a list of CAN messages, determine if the list of messages is valid or not, and print all errors that are found to the screen.
    write_id_probs -- Take a list of CAN frames along with a path to write a file to, and generate a dictionary of the probabilities of each ID occurring, and write it to a file. Return the dictionary of ID probabilities.
    load_id_probs -- Take the path to an ID probabilities file and return the ID probability dictionary from the file.
    inject_malicious_packets -- TBD
    generate_feature_lists -- Take in a list of CAN messages along with an ID probabilities dictionary and generate the feature lists required for the DNN based IDS.
    write_feature_lists -- Take in a list of features and the path to a file to write, and write a file containing the feature list to disk.
    load_feature_lists -- Take the path to a feature list file and return the feature lists from the file.
    """

    def parse_traffic(self, filepath):
        """Take in the path to a .traffic file, parse the file, and return a list of CAN messages.

        Arguments:
        filepath -- The path to the .traffic file. A FileNotFoundError will be thrown if the path given here is not valid. Additionally, a ValueError is thrown if the function is unable to parse the file because it is not a .traffic file.

        Returns a list of CAN messages in the format {'id': 1, 'timestamp': 1, 'data': b'\\x00\\x11'}.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath + ' does not exist!')
        elif os.path.isdir(filepath):
            raise FileNotFoundError(filepath + ' is not a file!')

        messages = []
        with open(filepath) as file:
            for line in file:
                escapedline = re.sub('0x[0-9A-F]+', r'"\g<0>"', line) # Surround instances of hex numbers with quotes: 0x9A -> "0x9A". Otherwise json.loads will fail.
                try:
                    message = json.loads(escapedline)
                except json.JSONDecodeError:
                    raise ValueError(filepath + ' does not appear to be a valid traffic file.')
                ts = int(message['timestamp']) # Timestamp may be given as integer or string, convert to integer. The timestamp is the UNIX timestamp in milliseconds.
                ts *= 10 # Convert to 0.1ms units instead of 1ms units. This is to make the value consistent with the CAN data format of the CSV files.

                if isinstance(message['id'], str): # ID may be given as hex or int, convert to int
                    id = int(message['id'], 16)
                else:
                    id = message['id']

                data = message['data']
                if isinstance(data[0], int):
                    # Data has been given as a list of signed byte integers. We convert these to the signed integer with the same hex representation as the unsigned integer. Ex. -1 -> 0xff -> 255.
                    data = list(map(lambda x: struct.unpack('B', struct.pack('b', x))[0], data))
                else:
                    # Data has been given as a list of hex values. We convert these to integers.
                    data = list(map(lambda x: int(x, 16), data))
                # At the end of the assignment, data is guaranteed to be a list of integers from 0-255. We can convert this to a bytes object, which is an immutable representation of a series of bytes.
                data = bytes(data)

                messages.append({'id': id, 'timestamp': ts, 'data': data})

        return messages

    def parse_csv(self, filepath):
        """Take in the path to a CAN frame .csv file, parse the file, and return a list of CAN messages.

        Arguments:
        filepath -- The path to the .traffic file. A FileNotFoundError will be thrown if the path given here is not valid. Additionally, a ValueError is thrown if the function is unable to parse the file because it is not a .traffic file.

        Returns a list of CAN messages in the format {'id': 1, 'timestamp': 1, 'data': b'\\x00\\x11'}.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath + ' does not exist!')
        elif os.path.isdir(filepath):
            raise FileNotFoundError(filepath + ' is not a file!')

        messages = []
        with open(filepath) as file:
            reader = csv.DictReader(file)
        for line in reader:
            try:
                ts = int(line['Time Stamp'], 16) # Timestamp is always given as hex, convert to int
                id = int(line['Frame ID'], 16) # Timestamp is always given as hex, convert to int
                datastring = line['Data'].strip('x| ') # Does "x| A2 C3 " -> "A2 C3"
            except KeyError:
                raise ValueError(filepath + ' does not appear to be a valid CAN packet csv file.')
            data = []
            for hexnum in datastring.split(' '):
                data.append(int(hexnum, 16)) # Does "01 00" (datastring) -> [1, 0] (data)
            data = bytes(data)

            messages.append({'id': id, 'timestamp': ts, 'data': data})

        return messages

    def validate_can_data(self, canlist):
        """Take in a list of CAN messages, determine if the list of messages is valid or not, and print all errors that are found to the screen.

        This function checks, in order:
         - If the list is empty
         - If every CAN message has the proper keys
         - If the ID is an integer in the range 0-2048
         - If the timestamp is a positive integer
         - If the data is a bytes object with length at most 8

        Arguments:
        canlist -- The list of CAN messages to validate.

        Returns a true/false value as to whether the list of messages is valid or not.
        """
        valid = True
        if len(canlist) == 0:
            print('The list provided is empty!')
            valid = False
        for i in range(len(canlist)):
            frame = canlist[i]
            # Does the frame have all the right keys?
            haskeys = True
            for key in ['id', 'timestamp', 'data']:
                if key not in frame:
                    print('Frame index {} does not have the key {}!'.format(i, repr(key)))
                    valid = False
                    haskeys = False
            if not haskeys:
                continue
            # Is the frame ID actually an integer?
            if not isinstance(frame['id'], int):
                print('Frame index {}\'s ID is not an integer: actually a {}, value {}!'.format(i, type(frame['id']), repr(frame['id'])))
                valid = False
            # Is the frame ID in the range 0-2047?
            elif frame['id'] < 0 or frame['id'] >= 2048:
                print('Frame index {}\'s ID is outside the range 0-2047: actually {}!'.format(i, frame['id']))
                valid = False
            # Is the timestamp actually an integer?
            if not isinstance(frame['timestamp'], int):
                print('Frame index {}\'s timestamp is not an integer: actually a {}, value {}!'.format(i, type(frame['timestamp']), repr(frame['timestamp'])))
                valid = False
            # Is the frame timestamp positive?
            elif frame['timestamp'] < 0:
                print('Frame index {}\'s timestamp is negative: actually {}!'.format(i, frame['timestamp']))
                valid = False
            # Is the data field a bytes object?
            # Note that data being a bytes object guarantees that the entries of the bytes are in the range 0-255, so this does not need to be verified.
            if not isinstance(frame['data'], bytes):
                print('Frame index {}\'s data is not a bytes object: actually a {}, value {}!'.format(i, type(frame['timestamp']), repr(frame['timestamp'])))
                valid = False
            # Is the data list 0-8 bytes long?
            elif len(frame['data']) > 8:
                print('Frame index {}\'s data field is longer than 8 bytes: actually {} bytes long!'.format(i, len(frame['data'])))
                valid = False

        if valid:
            print('This dataset is valid!')
        else:
            print('This dataset is invalid!')
        return valid

    def write_id_probs(self, canlist, outfilepath):
        """Take a list of CAN frames along with a path to write a file to, and generate a dictionary of the probabilities of each ID occurring, and write it to a file. Return the dictionary of ID probabilities.

        Arguments:
        canlist -- A list of CAN messages produced from parse_can or parse_traffic.
        outfilepath -- A string containing the path to the file you want to write. The file will be created by this function.

        This will write the dictionary of ID probabilities to the file specified in outfilepath in a JSON format, as well as return a dictionary where the key value pairs are id: probability of that id occurring.
        """
        idcounts = {}
        numframes = len(canlist)
        for frame in canlist:
            idcounts.setdefault(frame['id'], 0)
            idcounts[frame['id']] += 1

        probs = {k: v/numframes for k, v in idcounts.items()}
        with open(outfilepath, 'w+') as file:
            json.dump(probs, file, indent=2)
        return probs

    def load_id_probs(self, filepath):
        """Take the path to an ID probabilities file and return the ID probability dictionary from the file.

        Arguments:
        filepath -- The path to the ID probability file. A FileNotFoundError will be thrown if the path given here is not valid.

        This will return an ID probabilities dictionary where the key value pairs are id: probability of that id occurring.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath + ' does not exist!')
        elif os.path.isdir(filepath):
            raise FileNotFoundError(filepath + ' is not a file!')
        with open(filepath) as file:
            id_probs = json.load(file)
        # json.dump will make the entries of the dict look like "1": 0.4, so we must convert the keys to integers before we return the result.
        return {int(k): v for k, v in id_probs.items()}

    def inject_malicious_packets(self, canlist, malicious_packet_gen):
        pass

    def generate_feature_lists(self, canlist, idprobs):
        """Take in a list of CAN messages along with an ID probabilities dictionary and generate the feature lists required for the DNN based IDS.

        Arguments:
        canlist -- The list of CAN messages to use. Generated by parse_traffic and parse_csv.
        idprobs -- An ID probabilities list, generated by write_id_probs or load_id_probs.

        Returns a list of features, with the format {'id': [...], 'occurrences_in_last_sec': [...], 'relative_entropy': [...], 'system_entropy_change': [...]}.
        """
        featurelist = {'id': [], 'occurrences_in_last_sec': [], 'relative_entropy': [], 'system_entropy_change': []}
        frames_last_sec = []
        observed_idcounts = {}
        observed_numframes = 0
        total_numframes = len(canlist)
        observed_system_entropy = 0

        for frame in canlist:
            if observed_numframes % 100 == 0:
                print('{}/{} frames processed ({}%)'.format(observed_numframes, total_numframes, round(100*observed_numframes/total_numframes)), end='\r')
            id = frame['id']
            featurelist['id'].append(id)

            # Calculate the number of occurrences of the message in the last second
            ts = frame['timestamp']
            frames_last_sec = list(filter(lambda x: ts - x['timestamp'] < 10000, frames_last_sec)) # Get rid of frames older than 10000 0.1ms intervals (1 second)
            num_occurrences_id = 0
            for old_frame in frames_last_sec:
                if old_frame['id'] == id:
                    num_occurrences_id += 1
            featurelist['occurrences_in_last_sec'].append(num_occurrences_id)

            observed_numframes += 1
            observed_idcounts.setdefault(id, 0)
            observed_idcounts[id] += 1
            # Calculate relative entropy of message ID
            p = observed_idcounts[id] / observed_numframes
            q = idprobs.get(id, 0)
            if q == 0:
                featurelist['relative_entropy'].append(np.Infinity)
            else:
                featurelist['relative_entropy'].append(p * np.log(p / q))

            # Calculate change in system entropy
            old_system_entropy = observed_system_entropy
            observed_system_entropy = 0
            for k, v in observed_idcounts.items():
                p = v / observed_numframes
                with np.errstate(divide='ignore'):
                    observed_system_entropy -= p * np.log(p)
            featurelist['system_entropy_change'].append(observed_system_entropy - old_system_entropy)
            frames_last_sec.append(frame)

        return featurelist

    def write_feature_lists(self, featurelist, outfilepath):
        """Take in a list of features and the path to a file to write, and write a file containing the feature list to disk.

        Arguments:
        featurelist -- The list of features to write. Generated by generate_feature_lists.
        outfilepath -- A string containing the path to the file you want to write. The file will be created by this function.
        """
        with open(outfilepath, 'w+') as file:
            json.dump(featurelist, file, indent=2)

    def load_feature_lists(self, filepath):
        """Take the path to a feature list file and return the feature lists from the file.

        Arguments:
        filepath -- The path to the feature list file. A FileNotFoundError will be thrown if the path given here is not valid.

        This will return feature lists dictionary in the format {'id': [...], 'occurrences_in_last_sec': [...], 'relative_entropy': [...], 'system_entropy_change': [...]}.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath + ' does not exist!')
        elif os.path.isdir(filepath):
            raise FileNotFoundError(filepath + ' is not a file!')
        with open(filepath) as file:
            return json.load(file)