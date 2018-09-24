from NNIDS.canclass import CANMessage


# Returns .log file contents as [timestamp, [message id, message data]]
def log_parser(log_file_name):
    """
    Return .log file contents as a list of CANMessage objects

    :param log_file_name: name of .log file to parse
    :return: list of CANMessage objects
    :raises ValueError: if log_file_name does not contain '.log'
    """
    if log_file_name.find('.log') == -1:
        raise ValueError(log_file_name + ' does not appear to be a .log file')

    in_file = open(log_file_name)
    raw_data = [line.split(' ') for line in in_file]
    # timestamp, network_name, msg_id#msg_data
    in_file.close()

    msgs = []
    for packet in raw_data:
        temp = [packet[0], packet[2].split('#')]
        msgs.append(temp)

    can_msg_objs = []
    for line in msgs:
        ts_field = float(line[0][1:-1])  # Delete beginning and ending parentheses
        id_field = line[1][0]
        data_field = '0x' + line[1][1][:-1]  # Delete newline at end
        data_field = format(int(data_field, 16), '064b')  # 8 bytes of data
        can_msg_objs.append(CANMessage(ts_field, id_field, data_field))

    return can_msg_objs


def write_to_csv(csv_file_name, can_data):
    """
    Write list of CANMessage objects to a csv file
    with format 'timestamp, message id, message data'

    :param csv_file_name: name of csv file to write data to
    :param can_data: list of CANMssage objects
    :return: None
    :raises ValueError:
        if can_data is an empty list
        if '.csv' is not found in csv_file_name
    :raises TypeError: if can_data contains an object not of type CANMessage
    """
    if len(can_data) < 1:
        raise ValueError('can_data list is empty')
    if csv_file_name.find('.csv') == -1:
        raise ValueError('csv_file_name does not contain \'.csv\'')

    out_file = open(csv_file_name, 'w')
    for datum in can_data:
        if isinstance(datum, CANMessage) is False:
            raise TypeError('datum is not of type CANMessage')

        out_file.write('%s%s%s%s%s\n' % (datum.timestamp, ',',
                                         datum.id, ',', datum.data))
    out_file.close()
