class CANMessage:
    """ Class for representing a CAN message """
    def __init__(self, ts, msg_id, msg_data):
        """
        Generate a CANMessage object

        :param ts: timestamp of message
        :param msg_id: ID portion of CAN packet
        :param msg_data: data portion of CAN packet
        """
        self.timestamp = float(ts) # ts of the form '1504210534246'
        self.id = str(msg_id) # id of the form '042', it's already a string?!
        self.data = str(msg_data) # data is always '0x0', still already a string even though it's normally an array?!
        self.id_float = int('0x' + self.id, 16) # Why is this a separate attribute?!

    def __repr__(self):
        """
        Print CANMessage object

        :return: str representation of CANMessage object
        """
        return 'ID: 0x' + self.id + ' | DATA: 0x' \
               + str(hex(int(self.data, 2)))[2:].zfill(16) # Straight up does not work, 
                                                           # int(self.data, 2) will give you an error
