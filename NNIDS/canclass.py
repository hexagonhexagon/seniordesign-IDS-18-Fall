class CANMessage:
    """ Class for representing a CAN message """
    def __init__(self, ts, msg_id, msg_data):
        """
        Generate a CANMessage object

        :param ts: timestamp of message
        :param msg_id: ID portion of CAN packet
        :param msg_data: data portion of CAN packet
        """
        self.timestamp = float(ts)
        self.id = str(msg_id)
        self.data = str(msg_data)
        self.id_float = int('0x' + self.id, 16)

    def __repr__(self):
        """
        Print CANMessage object

        :return: str representation of CANMessage object
        """
        return 'ID: 0x' + self.id + ' | DATA: 0x' \
               + str(hex(int(self.data, 2)))[2:].zfill(16)
