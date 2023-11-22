
import can
import time
from mks_servo import MksServo
from mks_enums import CalibrationResult
from mks_enums import WorkMode
from mks_enums import SuccessStatus
from mks_enums import HoldingStrength
from mks_enums import EnPinEnable
from mks_enums import Direction
from mks_enums import Enable
from mks_enums import CanBitrate
from mks_enums import EndStopLevel
from mks_enums import GoHomeResult, Mode0

# TODO: It is a continuous call until result is 1 or 2?
def calibrate_encoder(self):
    rslt = self.set_generic(0x80, 0x00)
    try:
        rslt.status = CalibrationResult(rslt.status)
    except ValueError:
        print(f"No enum member with value {rslt.status}")     
        return None                   
    return rslt    
MksServo = calibrate_encoder(MksServo)

def set_work_mode(self, mode: WorkMode):
    return self.set_generic_status(0x82, mode)
MksServo = set_work_mode(MksServo)

def set_working_current(self, current):
    if current < 0 or current > 5200:
        print("Invalid current")
        return None    

    op_code = 0x83
    response_length = 3

    msg = self.create_can_msg(self.can_id, [op_code, (current >> 8) & 0xFF, current & 0xFF])

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
                        try:
                            status = SuccessStatus(status)
                        except ValueError:
                            print(f"No enum member with value {status}")     
                            return None                   
                        return {'status': status}
                    else:
                        print("Unexpected data length")
                        return None
            else:
                print("Invalid message CRC") 
MksServo = set_working_current(MksServo)

def set_holding_current(self, strength: HoldingStrength):
    return self.set_generic_status(0x9B, strength)    
MksServo = set_holding_current(MksServo)

def set_subdivision(self, mstep):
    return self.set_generic_status(0x84, mstep)    
MksServo = set_subdivision(MksServo)

def set_en_pin_config(self, enable: EnPinEnable):
    return self.set_generic_status(0x85, enable)     
MksServo = set_en_pin_config(MksServo)

def set_motor_rotation_direction(self, direction: Direction):
    return self.set_generic_status(0x86, direction)
MksServo = set_motor_rotation_direction(MksServo)

def set_auto_turn_off_screen(self, enable: Enable):
    return self.set_generic_status(0x87, enable)
MksServo = set_auto_turn_off_screen(MksServo)

def set_motor_shaft_locked_rotor_protection(self, enable: Enable):
    return self.set_generic_status(0x88, enable)
MksServo = set_auto_turn_off_screen(MksServo)

def set_subdivision_interpolation(self, enable: Enable):
    return self.set_generic_status(0x89, enable)
MksServo = set_subdivision_interpolation(MksServo)

def set_can_bitrate(self, bitrate: CanBitrate):
    return self.set_generic_status(0x8A, bitrate)
MksServo = set_can_bitrate(MksServo)

def set_can_id(self, can_id):
    return self.set_generic_status(0x8B, [(can_id >> 8) & 0xF, can_id & 0xFF])
MksServo = set_can_id(MksServo)

def set_slave_respond_active(self):
    print ("Not implemented")
MksServo = set_slave_respond_active(MksServo)

def set_key_lock_enable(self, enable: Enable):
    return self.set_generic_status(0x8F, enable)
MksServo = set_can_bitrate(MksServo)

def set_group_id(self, group_id):
    return self.set_generic_status(0x8D, [(group_id >> 8) & 0xF, group_id & 0xFF])
MksServo = set_can_id(MksServo)

def set_home(self, homeTrig : EndStopLevel, homeDir: Direction, homeSpeed, endLimit: Enable):
    return self.set_generic_status(0x90, [homeTrig, homeDir, (homeSpeed >> 8) & 0xF, homeSpeed & 0xFF, endLimit])
MksServo = set_home(MksServo)

def go_home(self):
    rslt = self.set_generic(0x91)
    try:
        rslt.status = GoHomeResult(rslt.status)
    except ValueError:
        print(f"No enum member with value {rslt.status}")     
        return None                   
    return rslt    
MksServo = go_home(MksServo)

def set_current_axis_to_zero(self):
    return self.set_generic_status(0x92)   
MksServo = go_home(MksServo)

def set_limit_port_remap(self, enable: Enable):
    return self.set_generic_status(0x9E, enable)   
MksServo = go_home(MksServo)    

def set_mode0(self, mode : Mode0, enable : Enable, speed, direction: Direction):
    cmd = [mode, enable, speed, direction]
    return self.set_generic_status(0x3F, [mode, enable, speed, direction])   
MksServo = set_mode0(MksServo)    

def restore_default_parameters(self):
    return self.set_generic_status(0x3F)   
MksServo = restore_default_parameters(MksServo)    