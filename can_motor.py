from mks_enums import Direction, Enable, SaveCleanState, RunMotorResult, MotorStatus
from mks_servo import MksServo

# constants
QUERY_MOTOR_STATUS_COMMAND = 0xF1
ENABLE_MOTOR_COMMAND = 0xF3
EMERGENCY_STOP_COMMAND = 0xF7
RUN_MOTOR_SPEED_MODE_COMMAND = 0xF6
SAVE_CLEAN_IN_SPEED_MODE_COMMAND = 0xFF
RUN_MOTOR_RELATIVE_MOTION_BY_PULSES_COMMAND = 0xFD
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

def _validate_direction(self, direction):
    if direction not in [Direction.CW, Direction.CCW]:
        raise invalid_direction_error("Direction must be CW or CCW")
MksServo = _validate_direction(MksServo)

def _validate_speed(self, speed):
    if speed < 0 or speed > MAX_SPEED:
        raise invalid_speed_error(f"Speed must be between 0 and {MAX_SPEED}")
MksServo = _validate_speed(MksServo)

def _validate_acceleration(self, acceleration):
    if acceleration < 0 or acceleration > MAX_ACCELERATION:
        raise invalid_aceleration_error(f"Acceleration must be between 0 and {MAX_ACCELERATION}")
MksServo = _validate_acceleration(MksServo)
    
def _validate_pulses(self, pulses):
    if pulses < 0 or pulses > MAX_PULSES:
        raise invalid_pulses_error("Pulses must be between 0 and 16777215")
MksServo = _validate_pulses(MksServo)


def query_motor_status(self):
    rslt = self.SetGeneric(QUERY_MOTOR_STATUS_COMMAND)
    try:
        rslt.status = MotorStatus(rslt.status)
    except ValueError:
        raise motor_status_error(f"No enum member with value {rslt.status}")                      
    return rslt            
MksServo = query_motor_status(MksServo)

def enable_motor(self, enable: Enable):
    return self.SetGenericStatus(ENABLE_MOTOR_COMMAND, enable)   
MksServo = enable_motor(MksServo)

def emergency_stop_motor(self):
    return self.SetGenericStatus(EMERGENCY_STOP_COMMAND)   
MksServo = emergency_stop_motor(MksServo)

def run_motor_in_speed_mode(self, direction: Direction, speed, acceleration, pulses,):
    _validate_direction(direction)
    _validate_speed(speed)
    _validate_acceleration(acceleration)

    direction_value = 0x80 if direction == Direction.CW else 0

    cmd = [
        direction_value + ((speed >> 8) & 0b1111),
        speed & 0xFF,
        acceleration
    ]
    return self.SetGenericStatus(RUN_MOTOR_SPEED_MODE_COMMAND, cmd)       
MksServo = run_motor_in_speed_mode(MksServo)

def save_clean_in_speed_mode(self, state: SaveCleanState):
    return self.SetGenericStatus(SAVE_CLEAN_IN_SPEED_MODE_COMMAND)   
MksServo = save_clean_in_speed_mode(MksServo)


def run_motor_relative_motion_by_pulses(self, direction: Direction, speed, acceleration, pulses):
    _validate_direction(direction)
    _validate_speed(speed)
    _validate_pulses(pulses)
  
    direction_value = 0x80 if direction == Direction.CW else 0

    cmd = [
        direction_value + ((speed >> 8) & 0b1111),
        speed & 0xFF,
        acceleration,
        (pulses >> 16) & 0xFF,
        (pulses >> 8) & 0xFF,
        (pulses >> 0) & 0xFF,
    ]
    rslt = self.SetGeneric(RUN_MOTOR_RELATIVE_MOTION_BY_PULSES_COMMAND, cmd)  
    try:
        rslt.status = RunMotorResult(rslt.status)
    except ValueError:
        raise motor_status_error(f"No enum member with value {rslt.status}")                     
    return rslt         
MksServo = run_motor_relative_motion_by_pulses(MksServo)

def run_motor_relative_motion_by_axis(self, speed, acceleration, relativeAxis):
    _validate_speed(speed)
    _validate_acceleration(acceleration)

    cmd = [
        ((speed >> 8) & 0b1111),
        speed & 0xFF,
        acceleration,        
        (relativeAxis >> 16) & 0xFF,
        (relativeAxis >> 8) & 0xFF,
        (relativeAxis >> 0) & 0xFF,
    ]
    rslt = self.SetGeneric(RUN_MOTOR_RELATIVE_MOTION_BY_AXIS_COMMAND, cmd)  
    try:
        rslt.status = RunMotorResult(rslt.status)
    except ValueError:
        raise motor_status_error(f"No enum member with value {rslt.status}")                                       
    return rslt    

def run_motor_absolute_motion_by_axis(self, speed, acceleration, absoluteAxis):
    _validate_speed(speed)
    _validate_acceleration(acceleration)
  
    cmd = [
        ((speed >> 8) & 0b1111),
        speed & 0xFF,
        acceleration,        
        (absoluteAxis >> 16) & 0xFF,
        (absoluteAxis >> 8) & 0xFF,
        (absoluteAxis >> 0) & 0xFF,
    ]
    rslt = self.SetGeneric(RUN_MOTOR_ABSOLUTE_MOTION_BY_AXIS_COMMAND, cmd)  
    try:
        rslt.status = RunMotorResult(rslt.status)
    except ValueError:
        raise motor_status_error(f"No enum member with value {rslt.status}")                                     
    return rslt    
