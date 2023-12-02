from mks_enums import Direction, Enable, SaveCleanState, RunMotorResult, MotorStatus
import time

# constants
QUERY_MOTOR_STATUS_COMMAND = 0xF1
ENABLE_MOTOR_COMMAND = 0xF3
EMERGENCY_STOP_COMMAND = 0xF7
RUN_MOTOR_SPEED_MODE_COMMAND = 0xF6
SAVE_CLEAN_IN_SPEED_MODE_COMMAND = 0xFF
RUN_MOTOR_RELATIVE_MOTION_BY_PULSES_COMMAND = 0xFD
RUN_MOTOR_ABSOLUTE_MOTION_BY_PULSES_COMMAND = 0xFE
RUN_MOTOR_RELATIVE_MOTION_BY_AXIS_COMMAND = 0xF4
RUN_MOTOR_ABSOLUTE_MOTION_BY_AXIS_COMMAND = 0xF5
MAX_SPEED = 3000
MAX_ACCELERATION = 255
MAX_PULSES = 0xFFFFFF

class invalid_direction_error(Exception):
    """Exception raised for invalid motor direction."""
    pass

class invalid_speed_error(Exception):
    """Exception raised for invalid motor speed."""
    pass

class invalid_aceleration_error(Exception):
    """Exception raised for invalid motor acceleration."""
    pass

class invalid_pulses_error(Exception):
    """Exception raised for invalid pulse count."""
    pass

class motor_status_error(Exception):
    """Exception raised for invalid motor status."""
    pass

class motor_already_running_error(Exception):
    """Exception raised for motor already running."""
    pass

def _validate_direction(self, direction):
    if direction not in [Direction.CW, Direction.CCW]:
        raise invalid_direction_error("Direction must be CW or CCW")

def _validate_speed(self, speed):
    if speed < 0 or speed > MAX_SPEED:
        raise invalid_speed_error(f"Speed must be between 0 and {MAX_SPEED}")

def _validate_acceleration(self, acceleration):
    if acceleration < 0 or acceleration > MAX_ACCELERATION:
        raise invalid_aceleration_error(f"Acceleration must be between 0 and {MAX_ACCELERATION}")
    
def _validate_pulses(self, pulses):
    if pulses < 0 or pulses > MAX_PULSES:
        raise invalid_pulses_error("Pulses must be between 0 and 16777215")


def query_motor_status(self): 
    tmp = self.set_generic(QUERY_MOTOR_STATUS_COMMAND, self.GENERIC_RESPONSE_LENGTH)  
    status_int = int.from_bytes(tmp[1:2], byteorder='big')  
    rslt = {}
    try:
        rslt['status'] = MotorStatus(status_int)
    except ValueError:
        raise motor_status_error(f"No enum member with value {status_int}")                     
    return rslt            

def enable_motor(self, enable: Enable):
    return self.set_generic_status(ENABLE_MOTOR_COMMAND, enable)   

def emergency_stop_motor(self):
    return self.set_generic_status(EMERGENCY_STOP_COMMAND)   

def run_motor_in_speed_mode(self, direction: Direction, speed, acceleration, pulses,):
    self._validate_direction(direction)
    self._validate_speed(speed)
    self._validate_acceleration(acceleration)

    direction_value = 0x80 if direction == Direction.CW else 0

    cmd = [
        direction_value + ((speed >> 8) & 0b1111),
        speed & 0xFF,
        acceleration
    ]
    return self.set_generic_status(RUN_MOTOR_SPEED_MODE_COMMAND, cmd)       

def save_clean_in_speed_mode(self, state: SaveCleanState):
    return self.set_generic_status(SAVE_CLEAN_IN_SPEED_MODE_COMMAND)   

def is_motor_running(self):
    return self._motor_run_status == RunMotorResult.RunStarting

def wait_for_motor_idle(self, timeout):    
    start_time = time.perf_counter()
    while (time.perf_counter() - start_time < timeout) and self.is_motor_running():
        time.sleep(0.1)  # Small sleep to prevent busy waiting
    return self.is_motor_running()

def run_motor_relative_motion_by_pulses(self, direction: Direction, speed, acceleration, pulses):
    if self.is_motor_running:
        raise motor_already_running_error("")    
    self._validate_direction(direction)
    self._validate_speed(speed)
    self._validate_pulses(pulses)
  
    direction_value = 0x80 if direction == Direction.CW else 0

    cmd = [
        direction_value + ((speed >> 8) & 0b1111),
        speed & 0xFF,
        acceleration,
        (pulses >> 16) & 0xFF,
        (pulses >> 8) & 0xFF,
        (pulses >> 0) & 0xFF,
    ]
    tmp = self.set_generic(RUN_MOTOR_RELATIVE_MOTION_BY_PULSES_COMMAND, self.GENERIC_RESPONSE_LENGTH, cmd)  
    status_int = int.from_bytes(tmp[1:2], byteorder='big')  
    rslt = {}
    try:
        rslt['status'] = RunMotorResult(status_int)
    except ValueError:
        raise motor_status_error(f"No enum member with value {status_int}")                     
    return rslt   

def run_motor_absolute_motion_by_pulses(self, speed, acceleration, pulses):
    if self.is_motor_running:
        raise motor_already_running_error("")    
    self._validate_speed(speed)
    self._validate_pulses(pulses)
  
    cmd = [
        (speed >> 8),
        speed & 0xFF,
        acceleration,
        (pulses >> 16) & 0xFF,
        (pulses >> 8) & 0xFF,
        (pulses >> 0) & 0xFF,
    ]
    tmp = self.set_generic(RUN_MOTOR_ABSOLUTE_MOTION_BY_PULSES_COMMAND, self.GENERIC_RESPONSE_LENGTH, cmd)  
    status_int = int.from_bytes(tmp[1:2], byteorder='big')  
    rslt = {}
    try:
        rslt['status'] = RunMotorResult(status_int)
    except ValueError:
        raise motor_status_error(f"No enum member with value {status_int}")                     
    return rslt      



def run_motor_relative_motion_by_axis(self, speed, acceleration, relativeAxis):
    if self.is_motor_running:
        raise motor_already_running_error("")    
    self._validate_speed(speed)
    self._validate_acceleration(acceleration)

    cmd = [
        ((speed >> 8) & 0b1111),
        speed & 0xFF,
        acceleration,        
        (relativeAxis >> 16) & 0xFF,
        (relativeAxis >> 8) & 0xFF,
        (relativeAxis >> 0) & 0xFF,
    ]
    tmp = self.set_generic(RUN_MOTOR_RELATIVE_MOTION_BY_AXIS_COMMAND, self.GENERIC_RESPONSE_LENGTH, cmd)  
    status_int = int.from_bytes(tmp[1:2], byteorder='big')  
    rslt = {}    
    try:
        rslt['status'] = RunMotorResult(status_int)
    except ValueError:
        raise motor_status_error(f"No enum member with value {status_int}")                                       
    return rslt    

def run_motor_absolute_motion_by_axis(self, speed, acceleration, absoluteAxis):
    if self.is_motor_running():
        raise motor_already_running_error("")    
    self._validate_speed(speed)
    self._validate_acceleration(acceleration)
  
    cmd = [
        ((speed >> 8) & 0b1111),
        speed & 0xFF,
        acceleration,        
        (absoluteAxis >> 16) & 0xFF,
        (absoluteAxis >> 8) & 0xFF,
        (absoluteAxis >> 0) & 0xFF,
    ]
    tmp = self.set_generic(RUN_MOTOR_ABSOLUTE_MOTION_BY_AXIS_COMMAND, self.GENERIC_RESPONSE_LENGTH, cmd)  
    status_int = int.from_bytes(tmp[1:2], byteorder='big')  
    rslt = {}    
    try:
        rslt['status'] = RunMotorResult(status_int)
    except ValueError:
        raise motor_status_error(f"No enum member with value {status_int}")                                     
    return rslt    

