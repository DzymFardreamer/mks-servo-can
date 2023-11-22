

import can
import time
import logging

from mks_enums import Enable, SuccessStatus

class CanMessageError(Exception):
    """Raised for errors related to CAN messaging."""
    pass

class InvalidCRCError(Exception):
    """Raised when CRC check fails."""
    pass

class ResponseTimeoutError(Exception):
    """Raised when response is not received within the expected timeout."""
    pass

class UnexpectedResponseLengthError(Exception):
    """Raised for unexpected response data length."""
    pass

class InvalidResponseError(Exception):
    """Raised for invalid response."""
    pass

class MksServo:
    """Controls MKS Servo via CAN messages.

    This class provides functionality to send commands to and receive responses from 
    an MKS Servo using CAN bus communication.

    Attributes:
        GENERIC_RESPONSE_LENGTH (int): Expected length of the generic response message.
        DEFAULT_TIMEOUT (int): Default timeout for waiting for a response in seconds.
        can_id (int): The CAN ID for this servo.
        bus (can.interface.Bus): The CAN bus instance to be used.
        timeout (int): Timeout for waiting for a response in seconds.
    """
    GENERIC_RESPONSE_LENGTH = 3
    DEFAULT_TIMEOUT = 1

    def __init__ (self, bus, id):
        """Inits MksServo with the CAN bus and servo ID.

        Args:
            bus (can.interface.Bus): The CAN bus instance to be used.
            can_id (int): The CAN ID for this servo.
        """        
        self.can_id = id
        self.bus = bus
        self.timeout = MksServo.DEFAULT_TIMEOUT

    def create_can_msg(self, msg):
        """Creates a CAN message with a CRC byte appended at the end.

        Args:
            msg (bytearray or list of bytes): The message data to which the CRC byte will be appended.

        Returns:
            can.Message: A CAN message object with the specified ID and data including the CRC byte.
        """

        # Calculate CRC and append to message
        crc = (self.can_id + sum(msg)) & 0xFF
        write_data = bytearray(msg) + bytes([crc])
        
        can_message = can.Message(arbitration_id=self.self.can_id, data=write_data, is_extended_id=False)            
        logging.debug(f"CAN Message Created: {can_message}")

        return can_message

    def check_msg_crc(self, msg):
        """Checks the CRC byte of a given CAN message for validity.

        Args:
            msg (can.Message): A CAN message object with an arbitration ID and data.

        Returns:
            bool: True if the last byte of the message data matches the calculated CRC, False otherwise.
        """

        logging.debug(f"Checking CRC for message: {msg}")

        # Calculate expected CRC and compare with the last byte of the message data
        crc = (msg.arbitration_id + sum(msg.data[:-1])) & 0xFF
        if msg.data[-1] != crc:
            raise InvalidCRCError("CRC check failed for the message.")    
            
        return True
    
    def set_generic(self, op_code, response_length, data = []):
        """Sends a generic command via CAN bus and waits for a response.

        Args:
            op_code (int): Operation code of the command.
            data (list of bytes, optional): Additional data for the command. Defaults to an empty list.

        Returns:
            dict: A dictionary with 'status' key if successful, None otherwise.
        """        
        msg = self.create_can_msg(self.can_id, [op_code] + data)

        # Flag to indicate whether the response has been received
        status = None

        def receive_message(message):
            nonlocal status

            if not status:
                try:
                    self.check_msg_crc(message)
                    if message.arbitration_id == self.can_id:
                        if not (message.data[0] == op_code and len(message.data) == response_length):
                            logging.error(f"Unexpected response length or opcode.")
                        
                        status = int.from_bytes(message.data, byteorder='big')                                         
                        self.bus.remove_listener(receive_message)
                except InvalidCRCError:
                    logging.error(f"CRC check failed for the message: {e}")            

        try:        
            self.bus.add_listener(receive_message)
            self.bus.send(msg)
        except can.CanError as e:
            raise CanMessageError(f"Error sending message: {e}")            

        # Wait for response (with a timeout)
        start_time = time.time()
        while time.time() - start_time < self.timeout and not status:
            time.sleep(0.1)  # Small sleep to prevent busy waiting
        self.bus.remove_listener(receive_message)

        return status
                      
    def set_generic_status(self, op_code, data = []):
        """Sends a generic status command and processes the response.

        Args:
            op_code (int): Operation code of the command.
            data (list of bytes, optional): Additional data for the command. Defaults to an empty list.

        Returns:
            dict: Modified result dictionary with 'status' key, None on error.
        """        
        result = self.set_generic(op_code, MksServo.GENERIC_RESPONSE_LENGTH, data)
        status_int = int.from_bytes(result[1:2], byteorder='big')  
        try:
            result.status = SuccessStatus(result.status)
        except ValueError:
            raise InvalidResponseError(f"No enum member with value {result['status']}")
               
        return result
    