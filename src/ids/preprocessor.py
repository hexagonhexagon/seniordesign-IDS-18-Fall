"""A module that handles preprocessing raw CAN message data and converting it
to feature sets.

Functions:
parse_traffic -- Take in the path to a .traffic file, parse the file, and
return a list of CAN messages.
parse_csv -- Take in the path to a CAN frame .csv file, parse the file, and
return a list of CAN messages.
write_canlist -- Take a list of CAN frames along with a path to write a file to,
and write the list of CAN frames to a file.
load_canlist -- Take the path to a CAN frame list file and return the CAN list
from the file.
validate_can_data -- Take in a list of CAN messages, determine if the list
of messages is valid or not, and print all errors that are found to the
screen.
write_id_probs -- Take a list of CAN frames along with a path to write a
file to, and generate a dictionary of the probabilities of each ID
occurring, and write it to a file. Return the dictionary of ID
probabilities.
load_id_probs -- Take the path to an ID probabilities file and return the ID
probability dictionary from the file.
inject_malicious_packets -- Take in a list of CAN messages and a malicious
generator and inject malicious packets into the list.
generate_feature_lists -- Take in a list of CAN messages along with an ID
probabilities dictionary and generate the feature lists required for the DNN
based IDS.
write_feature_lists -- Take in a list of features and the path to a file to
write, and write a file containing the feature list to disk.
load_feature_lists -- Take the path to a feature list file and return the
feature lists from the file.
"""

import collections
import csv
import json
import os.path
import re
import struct
from copy import deepcopy

import numpy as np


def parse_traffic(filepath):
    """Take in the path to a .traffic file, parse the file, and return a list
    of CAN messages.

    Arguments:
    filepath -- The path to the .traffic file. A
    FileNotFoundError will be thrown if the path given here is not valid.
    Additionally, a ValueError is thrown if the function is unable to parse
    the file because it is not a .traffic file.

    Returns a list of CAN messages in the format {'id': 1, 'timestamp': 1,
    'data': b'\\x00\\x11'}.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath + ' does not exist!')
    elif os.path.isdir(filepath):
        raise FileNotFoundError(filepath + ' is not a file!')

    messages = []
    with open(filepath) as file:
        for line in file:
            # Surround instances of hex numbers with quotes: 0x9A -> "0x9A".
            # Otherwise json.loads will fail.
            escapedline = re.sub('0x[0-9A-F]+', r'"\g<0>"', line)
            try:
                message = json.loads(escapedline)
            except json.JSONDecodeError:
                raise ValueError(
                    filepath + ' does not appear to be a valid traffic file.')
            # Timestamp may be given as integer or string, convert to
            # integer. The timestamp is the UNIX timestamp in milliseconds.
            ts = int(message['timestamp'])
            # Convert to 0.1ms units instead of 1ms units. This is to make
            # the value consistent with the CAN data format of the CSV
            # files.
            ts *= 10

            # ID may be given as hex or int, convert to int
            if isinstance(message['id'], str):
                id = int(message['id'], 16)
            else:
                id = message['id']

            data = message['data']
            if isinstance(data[0], int):
                # Data has been given as a list of signed byte integers. We
                # convert these to the signed integer with the same hex
                # representation as the unsigned integer. Ex. -1 -> 0xff ->
                # 255.
                data = list(
                    map(lambda x: struct.unpack('B', struct.pack('b', x))[0],
                        data))
            else:
                # Data has been given as a list of hex values. We convert
                # these to integers.
                data = list(map(lambda x: int(x, 16), data))
            # At the end of the assignment, data is guaranteed to be a list
            # of integers from 0-255. We can convert this to a bytes object,
            # which is an immutable representation of a series of bytes.
            data = bytes(data)

            messages.append({'id': id, 'timestamp': ts, 'data': data})

    return messages


def parse_csv(filepath):
    """Take in the path to a CAN frame .csv file, parse the file, and return a
    list of CAN messages.

    Arguments:
    filepath -- The path to the .traffic file. A
    FileNotFoundError will be thrown if the path given here is not valid.
    Additionally, a ValueError is thrown if the function is unable to parse
    the file because it is not a .traffic file.

    Returns a list of CAN messages in the format {'id': 1, 'timestamp': 1,
    'data': b'\\x00\\x11'}.
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
                # Timestamp is always given as hex, convert to int
                ts = int(line['Time Stamp'], 16)
                # Frame ID is always given as hex, convert to int
                id = int(line['Frame ID'], 16)
                # Does "x| A2 C3 " -> "A2 C3"
                datastring = line['Data'].strip('x| ')
            except KeyError:
                raise ValueError(
                    filepath +
                    ' does not appear to be a valid CAN packet csv file.')
            data = []
            for hexnum in datastring.split(' '):
                # Does "01 00" (datastring) -> [1, 0] (data)
                data.append(int(hexnum, 16))
            data = bytes(data)

            messages.append({'id': id, 'timestamp': ts, 'data': data})

    return messages


def write_canlist(canlist, outfilepath):
    """Take a list of CAN frames along with a path to write a file to, and
    and write the list of CAN frames to a file.

    Arguments:
    canlist -- A list of CAN messages produced from parse_can or
    parse_traffic.
    outfilepath -- A string containing the path to the file
    you want to write. The file will be created by this function.

    This will write the list of CAN frames to the file specified
    in outfilepath in a JSON format.
    """
    # A deep copy is performed to prevent the function from modifying canlist
    # outside of the call.
    writable_canlist = deepcopy(canlist)
    # JSON can't serialize the bytes objects in the 'data' field of CAN frames,
    # so we convert them to lists.
    for msg in writable_canlist:
        msg['data'] = list(msg['data'])
    with open(outfilepath, 'w+') as file:
        json.dump(writable_canlist, file, indent=2)


def load_canlist(filepath):
    """Take the path to a CAN frame list file and return the CAN list
    from the file.

    Arguments:
    filepath -- The path to the ID probability file. A
    FileNotFoundError will be thrown if the path given here is not valid.

    This will return a CAN frame list where each list item follows the format {'id': 1, 'timestamp': 1, 'data': b'\x00\x11'}.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath + ' does not exist!')
    elif os.path.isdir(filepath):
        raise FileNotFoundError(filepath + ' is not a file!')
    with open(filepath) as file:
        canlist = json.load(file)
    # The 'data' field for frames in the JSON file is a list, so we need to
    # convert it back to a bytes object.
    for msg in canlist:
        msg['data'] = bytes(msg['data'])
    return canlist



def validate_can_data(canlist):
    """Take in a list of CAN messages, determine if the list of messages is
    valid or not, and print all errors that are found to the screen.

    This function checks, in order:
        - If the list is empty
        - If every CAN message has the proper keys
        - If the ID is an integer in the range 0-2048
        - If the timestamp is a positive integer
        - If the data is a bytes object with length at most 8

    Arguments:
    canlist -- The list of CAN messages to validate.

    Returns a true/false value as to whether the list of messages is valid
    or not.
    """
    valid = True
    if len(canlist) == 0:
        print('The list provided is empty!')
        valid = False
    for i, frame in enumerate(canlist):
        # Does the frame have all the right keys?
        haskeys = True
        for key in ['id', 'timestamp', 'data']:
            if key not in frame:
                print('Frame index {} does not have the key {}!'.format(
                    i, repr(key)))
                valid = False
                haskeys = False
        if not haskeys:
            continue
        # Is the frame ID actually an integer?
        if not isinstance(frame['id'], int):
            print(
                'Frame index {}\'s ID is not an integer: actually a {}, value {}!'
                .format(i, type(frame['id']), repr(frame['id'])))
            valid = False
        # Is the frame ID in the range 0-2047?
        elif frame['id'] < 0 or frame['id'] >= 2048:
            print(
                'Frame index {}\'s ID is outside the range 0-2047: actually {}!'
                .format(i, frame['id']))
            valid = False
        # Is the timestamp actually an integer?
        if not isinstance(frame['timestamp'], int):
            print(
                'Frame index {}\'s timestamp is not an integer: actually a {}, value {}!'
                .format(i, type(frame['timestamp']), repr(frame['timestamp'])))
            valid = False
        # Is the frame timestamp positive?
        elif frame['timestamp'] < 0:
            print(
                'Frame index {}\'s timestamp is negative: actually {}!'.format(
                    i, frame['timestamp']))
            valid = False
        # Is the data field a bytes object? Note that data being a bytes
        # object guarantees that the entries of the bytes are in the range
        # 0-255, so this does not need to be verified.
        if not isinstance(frame['data'], bytes):
            print(
                'Frame index {}\'s data is not a bytes object: actually a {}, value {}!'
                .format(i, type(frame['timestamp']), repr(frame['timestamp'])))
            valid = False
        # Is the data list 0-8 bytes long?
        elif len(frame['data']) > 8:
            print(
                'Frame index {}\'s data field is longer than 8 bytes: actually {} bytes long!'
                .format(i, len(frame['data'])))
            valid = False

    if valid:
        print('This dataset is valid!')
    else:
        print('This dataset is invalid!')
    return valid


def write_id_probs(canlist, outfilepath=None):
    """Take a list of CAN frames along with a path to write a file to, and
    generate a dictionary of the probabilities of each ID occurring, and write
    it to a file. Return the dictionary of ID probabilities.

    Arguments:
    canlist -- A list of CAN messages produced from parse_can or
    parse_traffic.
    outfilepath -- A string containing the path to the file
    you want to write. The file will be created by this function.

    This will write the dictionary of ID probabilities to the file specified
    in outfilepath in a JSON format, as well as return a dictionary where
    the key value pairs are id: probability of that id occurring.
    """
    idcounts = collections.Counter()
    numframes = len(canlist)
    for frame in canlist:
        idcounts[frame['id']] += 1

    probs = {k: v / numframes for k, v in idcounts.items()}
    if outfilepath:
        with open(outfilepath, 'w+') as file:
            json.dump(probs, file, indent=2)
    return probs


def load_id_probs(filepath):
    """Take the path to an ID probabilities file and return the ID probability
    dictionary from the file.

    Arguments:
    filepath -- The path to the ID probability file. A
    FileNotFoundError will be thrown if the path given here is not valid.

    This will return an ID probabilities dictionary where the key value
    pairs are id: probability of that id occurring.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath + ' does not exist!')
    elif os.path.isdir(filepath):
        raise FileNotFoundError(filepath + ' is not a file!')
    with open(filepath) as file:
        id_probs = json.load(file)
    # json.dump will make the entries of the dict look like "1": 0.4, so we
    # must convert the keys to integers before we return the result.
    return {int(k): v for k, v in id_probs.items()}


def inject_malicious_packets(canlist, malgen):
    """Take in a list of CAN messages and a malicious generator and inject
    malicious packets into the list.

    Arguments:
    canlist -- The list of CAN messages to use. Generated by parse_traffic
    and parse_csv.
    malgen -- A MaliciousGenerator used to generate malicious packets to
    inject.

    Returns a tuple (newcanlist, labels), where newcanlist is the list of
    messages, and labels is a list of the labels for each message. Labels are
    'attack_name' if malicious, else None.
    """
    newcanlist = []
    # The labels for the frames. 0 means the packet is not malicious, and 1
    # means the packet is malicious. This is used later in the DNN based
    # IDS.
    labels = []
    for i in range(len(canlist) - 1):
        newcanlist.append(canlist[i])
        labels.append(None)
        malicious_frames = malgen.get((canlist[i], canlist[i + 1]))
        for frame, name in malicious_frames:
            newcanlist.append(frame)
            labels.append(name)
    newcanlist.append(canlist[-1])
    labels.append(None)
    return newcanlist, labels


class ID_Past:  # pylint: disable=too-few-public-methods,invalid-name
    """Calculates the frequency of each unique ID
    Frequency is calculated by counting the number of packets within the
    time_frame, including the current packet, and dividing by the length of the
    time_frame.
    This is a class, so that the memory queue can persist, which allows for
    feeding CAN frames in one-by-one.

    Attributes:
        time_frame: float distance in seconds to check back in time.

    Notes:
        CAN timestamps are in units of 0.1 miliseconds
    """

    def __init__(self, time_frame=1):
        self.time_frame = time_frame
        self.frame_q = collections.deque()
        self.id_counts = collections.Counter()

    def feed(self, canlist):
        """feed CAN frames into the counting queue.
        Args:
            canlist: a list of CAN packets; any length > 0
            time_frame: float distance in seconds to check back in time.
        Returns:
            A python generator, for each packet in canlist, yielding the
            frequency of the corresponding ID.
        """
        for frame in canlist:
            self.frame_q.append(frame)

            # Get rid of frames older than the time interval
            self.id_counts[frame['id']] += 1
            tdiff = self.frame_q[-1]['timestamp'] - self.frame_q[0]['timestamp']
            while tdiff >= self.time_frame * 1e4:
                pop_frame = self.frame_q.popleft()
                tdiff = self.frame_q[-1]['timestamp'] \
                        - self.frame_q[0]['timestamp']
                self.id_counts[pop_frame['id']] -= 1

            yield self.id_counts[frame['id']] / self.time_frame


class ID_Entropy:  # pylint: disable=too-few-public-methods,invalid-name
    """Calculate relative and system change entropy.
    This is a class, so that the memory queue can persist, which allows for
    feeding CAN frames in one-by-one.

    Returns:
        Two lists, containing the calculated relative and system change
        entropy, for each item in canlist
    """

    def __init__(self):
        self.observed_idcounts = collections.Counter()
        self.observed_system_entropy = 0

    def feed(self, canlist, idprobs):
        """feed CAN packets into entropy calculator
        Args:
            canlist: list of CAN packets; any length > 0
        Returns:
            python generator yielding tuples (e_relative, e_system)
        """
        for count, frame in enumerate(canlist, 1):
            self.observed_idcounts[frame['id']] += 1
            # Calculate relative entropy of message ID
            p = self.observed_idcounts[frame['id']] / count
            q = idprobs.get(frame['id'], 0)
            if q == 0:
                e_relative = 100
            else:
                e_relative = p * np.log(p / q)

            # Calculate change in system entropy
            old_system_entropy = self.observed_system_entropy
            self.observed_system_entropy = 0
            for v in self.observed_idcounts.values():
                p = v / count
                with np.errstate(divide='ignore'):
                    self.observed_system_entropy -= p * np.log(p)
            e_system = self.observed_system_entropy - old_system_entropy
            yield e_relative, e_system


def generate_feature_lists(canlist, idprobs):
    """Take in a list of CAN messages along with an ID probabilities dictionary
    and generate the feature lists required for the DNN based IDS.

    Arguments:
    canlist -- The list of CAN messages to use. Generated by parse_traffic
    and parse_csv.
    idprobs -- An ID probabilities list, generated by write_id_probs or
    load_id_probs.

    Returns a list of features, with the format {'id': [...],
    'occurrences_in_last_sec': [...], 'relative_entropy': [...],
    'system_entropy_change': [...]}.
    """
    featurelist = {
        'id': [x['id'] for x in canlist],
        'occurrences_in_last_sec': [],
        'relative_entropy': [],
        'system_entropy_change': []
    }

    featurelist['occurrences_in_last_sec'] = list(ID_Past().feed(canlist))
    # zip(*iterable) separates an iterable of length-N tuples into N tuples
    e_relative, e_system = zip(*ID_Entropy().feed(canlist, idprobs))
    featurelist['relative_entropy'] = list(e_relative)
    featurelist['system_entropy_change'] = list(e_system)

    return featurelist


def write_feature_lists(featurelist, labels, outfilepath):
    """Take in a list of features with their labels and the path to a file to
    write, and write a file containing the feature list to disk.

    Arguments:
    featurelist -- The list of features to write. Generated by
    generate_feature_lists.
    labels -- The list of labels for the feature list. Generated by
    inject_malicious_packets.
    outfilepath -- A string containing the path to the file you want to
    write. The file will be created by this function.
    """
    featureslabels = {'features': featurelist, 'labels': labels}
    with open(outfilepath, 'w+') as file:
        json.dump(featureslabels, file, indent=2)


def load_feature_lists(filepath):
    """Take the path to a feature list file and return the feature lists from
    the file.

    Arguments:
    filepath -- The path to the feature list file. A FileNotFoundError will
    be thrown if the path given here is not valid.

    This will return feature lists dictionary in the format {'id': [...],
    'occurrences_in_last_sec': [...], 'relative_entropy': [...],
    'system_entropy_change': [...]}.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath + ' does not exist!')
    elif os.path.isdir(filepath):
        raise FileNotFoundError(filepath + ' is not a file!')
    with open(filepath) as file:
        featurelist = json.load(file)
    return featurelist['features'], featurelist['labels']
