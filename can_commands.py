import time
import can
from mks_servo import MksServo

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

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        carry = int.from_bytes(data[1:5], byteorder='big', signed=True)
        value = int.from_bytes(data[5:7], byteorder='big', signed=True)
        return {'carry': carry, 'value': value}
    
    return None          
MksServo = read_encoder_value_carry(MksServo)

# Command 02: 
def read_encoder_value_addition(self):    
    op_code = 0x31
    response_length = 8

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        value = int.from_bytes(data[1:7], byteorder='big', signed=True)                        
        return {'value': value}    
    return None  
MksServo = read_encoder_value_addition(MksServo)

# Command 3
def read_motor_speed(self):
    op_code = 0x32
    response_length = 4

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        speed = int.from_bytes(data[1:3], byteorder='big', signed=True)                        
        return {'speed': speed} 
    return None  

MksServo = read_motor_speed(MksServo)

# Command 04
def read_num_pulses_received(self): 
    op_code = 0x33
    response_length = 6

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        pulses = int.from_bytes(data[1:5], byteorder='big', signed=True)                        
        return {'pulses': pulses}
    return None  

MksServo = read_num_pulses_received(MksServo)

# Command 06
def read_io_port_status(self):
    op_code = 0x34
    response_length = 3

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        status = int.from_bytes(data[1:2], byteorder='big')                        
        return {'status': status}
    return None  
MksServo = read_io_port_status(MksServo)

def read_motor_shaft_angle_error(self):
    op_code = 0x39
    response_length = 6

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        error = int.from_bytes(data[1:5], byteorder='big', signed=True)                        
        return {'error': error}
    return None  
MksServo = read_motor_shaft_angle_error(MksServo)

# command 6
def read_en_pins_status(self):
    op_code = 0x3A
    response_length = 3

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        enable = int.from_bytes(data[1:2], byteorder='big')                        
        return {'enable': enable}
    return None            
MksServo = read_en_pins_status(MksServo)

def read_go_back_to_zero_status_when_power_on(self):
    op_code = 0x3B
    response_length = 3

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        status = int.from_bytes(data[1:2], byteorder='big')                        
        return {'status': status}
    return None   
MksServo = read_go_back_to_zero_status_when_power_on(MksServo)

def release_motor_shaft_locked_protection_state(self):
    op_code = 0x3D
    response_length = 3

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        status = int.from_bytes(data[1:2], byteorder='big')                        
        return {'status': status}
    return None   
MksServo = release_motor_shaft_locked_protection_state(MksServo)

def read_motor_shaft_protection_state(self):
    op_code = 0x3E
    response_length = 3

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        enable = int.from_bytes(data[1:2], byteorder='big')                        
        return {'enable': enable}
    return None             
MksServo = read_motor_shaft_protection_state(MksServo)
