
import can
import time
#from mks_servo import MksServo
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

class gohome_status_error(Exception):
    """Exception raised for invalid gohome status."""
    pass

class current_error(Exception):
    """Exception raised for invalid motor status."""
    pass

def _validate_current(self, current):
    if current < 0 or current > 5200:
        raise current_error("Current is outside the valid range from 0 to 5200")
    
# TODO: It is a continuous call until result is 1 or 2?
def calibrate_encoder(self):
    rslt = self.set_generic(0x80, 0x00)
    try:
        rslt.status = CalibrationResult(rslt.status)
    except ValueError:
        print(f"No enum member with value {rslt.status}")     
        return None                   
    return rslt    

def set_work_mode(self, mode: WorkMode):
    return self.set_generic_status(0x82, mode.value)

def set_working_current(self, current):
    self._validate_current(current)
    return self.set_generic_status(0x83, [(current >> 8) & 0xFF, current & 0xFF])    

def set_holding_current(self, strength: HoldingStrength):
    return self.set_generic_status(0x9B, strength.value)    

def set_subdivision(self, mstep):
    return self.set_generic_status(0x84, mstep)    

def set_en_pin_config(self, enable: EnPinEnable):
    return self.set_generic_status(0x85, enable.value)     

def set_motor_rotation_direction(self, direction: Direction):
    return self.set_generic_status(0x86, direction.value)

def set_auto_turn_off_screen(self, enable: Enable):
    return self.set_generic_status(0x87, enable.value)

def set_motor_shaft_locked_rotor_protection(self, enable: Enable):
    return self.set_generic_status(0x88, enable.value)

def set_subdivision_interpolation(self, enable: Enable):
    return self.set_generic_status(0x89, enable.value)

def set_can_bitrate(self, bitrate: CanBitrate):
    return self.set_generic_status(0x8A, bitrate.value)

def set_can_id(self, can_id):
    return self.set_generic_status(0x8B, [(can_id >> 8) & 0xF, can_id & 0xFF])

def set_slave_respond_active(self):
    print ("Not implemented")

def set_key_lock_enable(self, enable: Enable):
    return self.set_generic_status(0x8F, enable.value)

def set_group_id(self, group_id):
    return self.set_generic_status(0x8D, [(group_id >> 8) & 0xF, group_id & 0xFF])

def set_home(self, homeTrig : EndStopLevel, homeDir: Direction, homeSpeed, endLimit: Enable):
    return self.set_generic_status(0x90, [homeTrig, homeDir, (homeSpeed >> 8) & 0xF, homeSpeed & 0xFF, endLimit])

def go_home(self):
    tmp = self.set_generic(0x91, self.GENERIC_RESPONSE_LENGTH)
    status_int = int.from_bytes(tmp[1:2], byteorder='big')  
    rslt = {}
    try:
        rslt['status'] = GoHomeResult(status_int)
    except ValueError:
        raise gohome_status_error(f"No enum member with value {status_int}")                     
    return rslt   

def set_current_axis_to_zero(self):
    return self.set_generic_status(0x92)   

def set_limit_port_remap(self, enable: Enable):
    return self.set_generic_status(0x9E, enable.value)   

def set_mode0(self, mode : Mode0, enable : Enable, speed, direction: Direction):
    cmd = [mode, enable.value, speed, direction.value]
    return self.set_generic_status(0x3F, [mode, enable, speed, direction])   

def restore_default_parameters(self):
    return self.set_generic_status(0x3F)   
