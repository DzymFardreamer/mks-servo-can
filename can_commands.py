
import can
import time
from mks_enums import Direction

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


    def read_encoder_value_carry(self):
        """
        Reads encoder values from a CAN self.bus using a specific CAN ID and operation code.

        This function sends a CAN message with a predefined operation code to request encoder values.
        It waits for a response message with specific data format and length. If the response is valid and
        matches the expected criteria, it extracts and returns the 'carry' and 'value' from the encoder.

        The value is in the range of 0 to 0x3FFF.
        When value is less than 0, carry -= 1    

        Args:
        - self.can_id (int, optional): The CAN ID to be used for sending the request and matching the response. 
        Defaults to 1.

        Returns:
        - dict or None: If successful, returns a dictionary with 'carry' and 'value' from the encoder. 
        Returns None if there's an error in sending the message, a self.timeout occurs, or the response is 
        invalid.

        Raises:
        - can.CanError: If there is an error in sending the CAN message.

        Note:
        - The function assumes that a CAN self.bus object 'self.bus' and a self.timeout value 'self.timeout' are already defined in the scope where this function is called.
        """
        op_code = 0x30
        response_length = 8

        # Create and send CAN message
        msg = self.create_can_msg(self.can_id, [op_code])
        try:
            self.bus.send(msg)
        except can.CanError:
            print("Error while sending message")
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
                            # Extract 'carry' and 'value' from the response
                            carry = int.from_bytes(message.data[1:5], byteorder='big', signed=True)
                            value = int.from_bytes(message.data[5:7], byteorder='big', signed=True)
                            return {'carry': carry, 'value': value}
                        else:
                            print("Unexpected data length")
                            return None
                else:
                    print("Invalid message CRC")
        return None

    # Command 02: 
    def read_encoder_value_addition(self):    
        op_code = 0x31
        response_length = 8

        msg = self.create_can_msg(self.can_id, [op_code])

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
                            value = int.from_bytes(message.data[1:7], byteorder='big', signed=True)                        
                            return {'value': value}
                        else:
                            print("Unexpected data length")
                            return None
                else:
                    print("Invalid message CRC")

    # Command 3
    def read_motor_speed(self):
        op_code = 0x32
        response_length = 4

        msg = self.create_can_msg(self.can_id, [op_code])

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
                            speed = int.from_bytes(message.data[1:3], byteorder='big', signed=True)                        
                            return {'speed': speed}
                        else:
                            print("Unexpected data length")
                            return None
                else:
                    print("Invalid message CRC")

    # Command 04
    def read_num_pulses_recieved(self): 
        op_code = 0x33
        response_length = 6

        msg = self.create_can_msg(self.can_id, [op_code])

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
                            pulses = int.from_bytes(message.data[1:5], byteorder='big', signed=True)                        
                            return {'pulses': pulses}
                        else:
                            print("Unexpected data length")
                            return None
                else:
                    print("Invalid message CRC")

    # Command 06
    def read_io_port_status(self):
        op_code = 0x34
        response_length = 3

        msg = self.create_can_msg(self.can_id, [op_code])

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

    def read_motor_shaft_angle_error(self):
        op_code = 0x39
        response_length = 6

        msg = self.create_can_msg(self.can_id, [op_code])

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
                            error = int.from_bytes(message.data[1:5], byteorder='big', signed=True)                        
                            return {'error': error}
                        else:
                            print("Unexpected data length")
                            return None
                else:
                    print("Invalid message CRC")    

    # command 6
    def read_en_pins_status(self):
        op_code = 0x3A
        response_length = 3

        msg = self.create_can_msg(self.can_id, [op_code])

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
                            enable = int.from_bytes(message.data[1:2], byteorder='big')                        
                            return {'enable': enable}
                        else:
                            print("Unexpected data length")
                            return None
                else:
                    print("Invalid message CRC")        

    def read_go_back_to_zero_status_when_power_on(self):
        op_code = 0x3B
        response_length = 3

        msg = self.create_can_msg(self.can_id, [op_code])

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

    def release_motor_shaft_locked_protection_state(self):
        op_code = 0x3D
        response_length = 3

        msg = self.create_can_msg(self.can_id, [op_code])

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

    def read_motor_shaft_protection_state(self):
        op_code = 0x3E
        response_length = 3

        msg = self.create_can_msg(self.can_id, [op_code])

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
                            enable = int.from_bytes(message.data[1:2], byteorder='big')                        
                            return {'enable': enable}
                        else:
                            print("Unexpected data length")
                            return None
                else:
                    print("Invalid message CRC")               

    def calibrate_encoder():
        #CMD: 80 00, returns 80, status(uint8_t)
        return None   

    def query_motor_status(self):
        op_code = 0xF1
        response_length = 3

        msg = self.create_can_msg(self.can_id, [op_code])

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

    def enable_motor(self, enable,):
        op_code = 0xF3
        response_length = 3

        msg = self.create_can_msg(self.can_id, [op_code, 0x01 if enable else 0x00])

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



    def run_motor_speed_mode(self, dir: Direction, speed, acceleration, pulses,):
        if not (dir == Direction.CW or dir == Direction.CCW):    
            print("Invalid direction")
            return None

        if speed < 0 or speed > 3000:
            print("Invalid speed")
            return None

        op_code = 0xF6
        response_length = 3

        # Check the direction and add 0x80 if CW
        dir_value = 0x80 if dir == Direction.CW else 0

        # Construct the command
        cmd = [
            op_code,
            dir_value + ((speed >> 8) & 0b1111),
            speed & 0xFF,
            acceleration
        ]

        
        msg = self.create_can_msg(self.can_id, cmd)

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
                            status = int.from_bytes(message.data[1:2], byteorder='big', signed=True)                        
                            return {'status': status}
                        else:
                            print("Unexpected data length")
                            return None
                else:
                    print("Invalid message CRC")

    def run_motor_relative_motion_by_pulses(self, dir: Direction, speed, acceleration, pulses):
        if not (dir == Direction.CW or dir == Direction.CCW):    
            print("Invalid direction")
            return None

        if speed < 0 or speed > 3000:
            print("Invalid speed")
            return None

        if pulses < 0 or pulses > 0xFFFFFF:
            print("Invalid pulses")
            return None

        op_code = 0xFD
        response_length = 3

        # Check the direction and add 0x80 if CW
        dir_value = 0x80 if dir == Direction.CW else 0

        # Construct the command
        cmd = [
            op_code,
            dir_value + ((speed >> 8) & 0b1111),
            speed & 0xFF,
            acceleration,
            (pulses >> 16) & 0xFF,
            (pulses >> 8) & 0xFF,
            (pulses >> 0) & 0xFF,
        ]

        
        msg = self.create_can_msg(self.can_id, cmd)

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
                            status = int.from_bytes(message.data[1:2], byteorder='big', signed=True)                        
                            return {'status': status}
                        else:
                            print("Unexpected data length")
                            return None
                else:
                    print("Invalid message CRC")
