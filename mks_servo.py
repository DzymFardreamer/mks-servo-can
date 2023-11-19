

import can
import time

from mks_enums import Enable
from mks_enums import SuccessStatus

class MksServo:
    def __init__ (self, bus, id):
        self.self.can_id = id
        self.bus = self.bus
        self.timeout = 1

    def create_can_msg(self, msg):
        """
        Creates a CAN message with a CRC byte appended at the end.

        This function calculates a CRC (Cyclic Redundancy Check) byte by adding the given CAN ID to
        the sum of all bytes in the message.
        The sum is then subjected to a bitwise AND operation with 0xFF. This CRC byte is appended to
        the end of the message.
        A CAN message object is then created with the specified arbitration ID and the byte array that
        includes the CRC byte.

        Args:
        - self.can_id (int): The CAN ID to be used as the arbitration ID for the message.
        - msg (bytearray or list of bytes): The message data to which the CRC byte will be appended.

        Returns:
        - can.Message: A CAN message object with the specified ID and data including the CRC byte.
        """

        # Calculate CRC and append to message
        crc = (self.self.can_id + sum(msg)) & 0xFF
        write_data = bytearray(msg) + bytes([crc])

        # Create CAN message object
        can_message = can.Message(arbitration_id=self.self.can_id, data=write_data, is_extended_id=False)
        
        # Print message for debugging
        print(can_message, flush=True)

        return can_message

    def check_msg_crc(self, msg):
        """
        Checks the CRC byte of a given CAN message for validity.

        This function calculates the expected CRC byte by adding the arbitration ID to the sum of all
        but the last byte of the message data.
        The sum is then subjected to a bitwise AND operation with 0xFF. This calculated CRC is then 
        compared to the last byte of the message
        to verify if the CRC is correct.

        Args:
        - msg (can.Message): A CAN message object with an arbitration ID and data. The data should 
        include the CRC byte at the end.

        Returns:
        - bool: True if the last byte of the message data matches the calculated CRC, False otherwise.
        """

        # Print message for debugging
        print(msg)

        # Calculate expected CRC and compare with the last byte of the message data
        crc = (msg.arbitration_id + sum(msg.data[:-1])) & 0xFF
        return msg.data[-1] == crc

    def SetGeneric(self, op_code, data = []):
        response_length = 3

        # TODO, data can be an array or a single byte
        msg = self.create_can_msg(self.can_id, [op_code, data])

        try:        
            self.bus.send(msg)
        except can.CanError:
            print("Error al enviar mensaje")
            return None

        # Wait for the response
        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout:
                print("self.timeout")
                return None

            message = self.bus.recv(0.1) 
            if message:
                if self.check_msg_crc(message):
                    if message.arbitration_id == self.can_id:
                        if message.data[0] == op_code and len(message.data) == response_length:
                            status = int.from_bytes(message.data[1:2], byteorder='big')                                         
                            return {'status': status}
                        else:
                            print("Unexpected data length")
                            return None
                else:
                    print("Invalid message CRC") 
            
    def SetGenericStatus(self, op_code, data = []):
        rslt = self.SetGeneric(op_code, data)
        try:
            rslt.status = SuccessStatus(rslt.status)
        except ValueError:
            print(f"No enum member with value {rslt.status}")     
            return None                   
        return rslt