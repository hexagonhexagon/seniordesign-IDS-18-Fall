from NNIDS.canclass import CANMessage


def traffic_parser(log_file_name):
    """
    Return contents of .traffic file as array of CANMessage objects.

    :param log_file_name: name of .traffic file to parse
    :return: list of CANMessage objects
    :raises ValueError: if '.traffic' is not found in log_file_name
    """
    if log_file_name.find('.traffic') == -1:
        raise ValueError(log_file_name + ' does not appear to be a .traffic file')

    in_file = open(log_file_name)
    raw_data = [line.split(',') for line in in_file if line.find('comment') == -1]
    # timestamp, seq, msg_id#msg_data
    in_file.close()

    msgs = []
    for packet in raw_data:
        read_id = packet[2].split(':')[1]
        read_id = read_id[read_id.find('x') + 1:]
        x = 3 - len(read_id)
        for i in range(0, x):
            read_id = '0' + read_id

        temp = [packet[0].split(':')[1], read_id]
        msgs.append(temp)

    can_msg_objs = []
    for line in msgs:
        ts_field = float(line[0][1:-1])  # Delete beginning and ending quotes
        # ts_field = float(line[0])
        id_field = line[1]
        data_field = '0x0'
        can_msg_objs.append(CANMessage(ts_field, id_field, data_field))

    return can_msg_objs
