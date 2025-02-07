
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
from mks_enums import MksCommands
from mks_enums import GoHomeResult, Mode0

class gohome_status_error(Exception):
    """Exception raised for invalid gohome status."""
    pass

class calibration_error(Exception):
    """Exception raised for invalid gohome status."""
    pass

class current_error(Exception):
    """Exception raised for invalid motor status."""
    pass

class calibration_not_running(Exception):
    """Exception raised for calibration not running status."""
    pass

class calibration_timeout_error(Exception):
    """Exception raised for calibraton timeout status."""
    pass

class go_home_timeout_error(Exception):
    """Exception raised for go home timeout status."""
    pass

def _validate_current(self, current):
    if current < 0 or current > 5200:
        raise current_error("Current is outside the valid range from 0 to 5200")
    
# TODO: It is a continuous call until result is 1 or 2?
def nb_calibrate_encoder(self):
    """
    Initiates the calibration procedure of the encoder.

    Returns:
        CalibrationResult: The success result of the command. It should be "Calibrating".

    Raises:
        can.CanError: If there is an error in sending the CAN message.    
    """       
    tmp = self.set_generic(MksCommands.MOTOR_CALIBRATION_COMMAND, self.GENERIC_RESPONSE_LENGTH, 0x00)
    status_int = int.from_bytes(tmp[1:2], byteorder='big')      
    try:
        rslt = CalibrationResult(status_int)
        self._calibration_status = rslt
        return rslt
    except ValueError:
        raise calibration_error(f"No enum member with value {status_int}")                     

def b_calibrate_encoder(self):
    """
    Does the calibration procedure of the encoder. It blocks until the procedure completes.

    Returns:
        CalibrationResult: The success result of the command. It should be "CalibratedSuccess" or "CalibratingFail".

    Raises:
        can.CanError: If there is an error in sending the CAN message.    
    """      
    nb_calibrate_encoder(self) 
    wait_for_calibration(self)
    return self._calibration_status

def wait_for_calibration(self):
    """
    Waits until the calibration procedure completes.

    Returns:
        CalibrationResult: The success result of the command. It should be "CalibratedSuccess" or "CalibratingFail".

    Raises:
        can.CanError: If there is an error in sending the CAN message.    
        calibration_timeout_error: If the calibration took longer than the expected time.
    """     
    if self._calibration_status == CalibrationResult.Unkown:
        raise calibration_not_running("")

    start_time = time.perf_counter()
    while (time.perf_counter() - start_time < self.MAX_CALIBRATION_TIME) and self._calibration_status == CalibrationResult.Calibrating:
        time.sleep(0.1)  # Small sleep to prevent busy waiting

    if not self._calibration_status == CalibrationResult.CalibratedSuccess and not self._calibration_status == CalibrationResult.CalibratingFail:
        raise calibration_timeout_error("")      
    
    return self._calibration_status

def set_work_mode(self, mode: WorkMode):
    """
    Set the working mode of the servo.

    Args:        
        mode (WorkMode): The mode of the servo

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.    

    Note: Setting CrOpen, CrClose or CrvFoc will lose communication over CAN.
    """       
    return self.set_generic_status(MksCommands.SET_WORK_MODE_COMMAND, mode.value)

def set_working_current(self, current):
    """
    Sets the working current.

    Args:        
        current (int): The working current in miliamps.

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.    

    Note: The maximum current for Servo42D, 28D and 35D is 3000 mA. The maximum current for servod57d is 5200 ma.
    """      
    self._validate_current(current)
    return self.set_generic_status(MksCommands.SET_WORKING_CURRENT_COMMAND, [(current >> 8) & 0xFF, current & 0xFF])    

def set_holding_current(self, strength: HoldingStrength):
    """
    Sets the holding current.

    Args:        
        strength (HoldingStrength): Sets the holding current percentage.

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.    

    Note: Only for OPEN and CLOSE mode, vFOC mode is invalid.
    """          
    return self.set_generic_status(MksCommands.SET_HOLDING_CURRENT_COMMAND, strength.value)    

def set_subdivisions(self, mstep):
    """
    Sets the subdivisions

    Args:        
        mstep (int): The subdivisions

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        
    """      
    return self.set_generic_status(MksCommands.SET_SUBDIVISIONS_COMMAND, mstep)    

def set_en_pin_config(self, enable: EnPinEnable):
    """
    Sets the active of the enable pins

    Args:        
        enable (EnPinEnable): The active mode.

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        
    """        
    return self.set_generic_status(MksCommands.SET_EN_PIN_CONFIG_COMMAND, enable.value)     

def set_motor_rotation_direction(self, direction: Direction):
    """
    Sets the direction of motor rotation

    Args:        
        direction (Direction): The direction

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        

    Note: Only for pulse interface, the direction of serial interface is set by command.
    """          
    return self.set_generic_status(MksCommands.SET_MOTOR_ROTATION_DIRECTION, direction.value)

def set_auto_turn_off_screen(self, enable: Enable):
    """
    Sets the auto turn off function of the screen

    Args:        
        enable (Enable): The enable value.

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        

    Note: If set to Enable, the screen will automatically turn off after about 15 seconds, and
        any button can wake up the screen again.
    """       
    return self.set_generic_status(MksCommands.SET_AUTO_TURN_OFF_SCREEN_COMMAND, enable.value)

def set_motor_shaft_locked_rotor_protection(self, enable: Enable):
    """
    Sets the motor shaft protection

    Args:        
        enable (Enable): The enable value.

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        

    Note: Same as the "Protect" option on screen.
    """     
    return self.set_generic_status(MksCommands.SET_MOTOR_SHAFT_LOCKED_ROTOR_PROTECTION_COMMAND, enable.value)

def set_subdivision_interpolation(self, enable: Enable):
    """
    Sets the subdivision interpolation function.

    Args:        
        enable (Enable): The enable value for the interpolation..

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        

    Note: Same as the "Mplyer" option on screen.
    """       
    return self.set_generic_status(MksCommands.SET_SUBDIVISION_INTERPOLATION_COMMAND, enable.value)

def set_can_bitrate(self, bitrate: CanBitrate):
    """
    Sets the can bitrate

    Args:        
        bitrate (CanBitrate): The can bitrate

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        

    Note: Same as the "CanRate" option on screen.
    """        
    return self.set_generic_status(MksCommands.SET_CAN_BITRATE_COMMAND, bitrate.value)

def set_can_id(self, can_id):
    """
    Set the can id

    Args:        
        can_id (int): The can id

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        

    Note: Same as the "CanID" option on screen.
    """        
    return self.set_generic_status(MksCommands.SET_CAN_ID, [(can_id >> 8) & 0xF, can_id & 0xFF])

def set_slave_respond_active(self, respon, active):
    """
    Sets the slave respond and active

    Args:        
        respon (Enable): 
        active (Enable): 

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        

    Note: Not implemented
    """         
    print ("Not implemented")

def set_key_lock(self, enable: Enable):
    """
    Set the key lock

    Args:        
        enable (Enable): The status of the key lock

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.            
    """       
    return self.set_generic_status(MksCommands.SET_KEY_LOCK_ENABLE_COMMAND, enable.value)

def set_group_id(self, group_id):
    """
    Sets the group id

    Args:        
        group_id (int): The group id

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        
    
    """     
    return self.set_generic_status(MksCommands.SET_GROUP_ID_COMMAND, [(group_id >> 8) & 0xF, group_id & 0xFF])

def set_home(self, homeTrig : EndStopLevel, homeDir: Direction, homeSpeed, endLimit: Enable):
    """
    Sets the parameter of Home

    Args:        
        homeTrig (EndStopLevel): The effective level of the end stop
        homeDir (Direction): The direction of go home
        homeSpeed (int): The speed of go home
        endLimit (Enable): The end limit enable status.

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        

    Note: Same as the "HmTrig", "HmDir" and "HmSpeed" options on screen.

    Note: When first time to using the endLimit function or changing the limit paramters, it is necessary to go home.
    """       
    return self.set_generic_status(MksCommands.SET_HOME_COMMAND, [homeTrig.value, homeDir.value, (homeSpeed >> 8) & 0xF, homeSpeed & 0xFF, endLimit.value])

def nb_go_home(self):
    """
    Goes home

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        

    Note: Same as the "CanID" option on screen.
    """       
    tmp = self.set_generic(MksCommands.GO_HOME_COMMAND, self.GENERIC_RESPONSE_LENGTH)
    status_int = int.from_bytes(tmp[1:2], byteorder='big')  
    try:
        rslt = GoHomeResult(status_int)
        self._homing_status = rslt
    except ValueError:
        raise gohome_status_error(f"No enum member with value {status_int}")                     
    return rslt   

def b_go_home(self):
    """
    Does the calibration procedure of the encoder. It blocks until the procedure completes.

    Returns:
        GoHomeResult: The success result of the command. It should be "Success" or "Fail".

    Raises:
        can.CanError: If there is an error in sending the CAN message.    
    """      
    nb_go_home(self) 
    wait_for_go_home(self)
    return self._homing_status

def wait_for_go_home(self):
    """
    Waits until the go home procedure completes.

    Returns:
        GoHomeResult: The success result of the command. It should be "Success" or "Fail".

    Raises:
        can.CanError: If there is an error in sending the CAN message.    
        go_home_timeout_error: If the go home operation took longer than the expected time.
    """     
    if self._homing_status == GoHomeResult.Unkown:
        raise calibration_not_running("")

    start_time = time.perf_counter()
    while (time.perf_counter() - start_time < self.MAX_HOMING_TIME) and self._homing_status == GoHomeResult.Start:
        time.sleep(0.1)  # Small sleep to prevent busy waiting

    if not self._homing_status == GoHomeResult.Success and not self._homing_status == GoHomeResult.Fail:
        raise go_home_timeout_error("")      
    
    return self._homing_status

def set_current_axis_to_zero(self):
    """
    Sets current axis to zero. It is like "go_home" without running the motor.

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        
    """       
    return self.set_generic_status(MksCommands.SET_CURRENT_AXIS_TO_ZERO_COMMAND)   

def set_limit_port_remap(self, enable: Enable):
    """
    Sets the limit port remap. The 28/35/42D motors only have a left limit port.
    In serial control mode, limit port remapping can be enabled to add a right limit port.
    For the 57D motor, limit port remapping can also be enabled if required to facilitate wiring.
    Left limit -> En port
    Right limit -> Dir port.
    The com port must be connected to the corresponding high level.

    Args:        
        enable (Enable): The enable status.

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.            
    """       
    return self.set_generic_status(MksCommands.SET_LIMIT_PORT_REMAP_COMMAND, enable.value)   

def set_mode0(self, mode : Mode0, enable : Enable, speed, direction: Direction):
    """
    Sets mode 0 where the motor can automatically return to the 0 point position when power on.
    The maximum angle is 359 degrees.

    Args:        
        mode (Mode0): The mode
        enable (Enable): The enable status
        speed (int): Speed. 0: slowest, 4: fastest
        direction (Direction): The direction

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.            
    """       
    cmd = [mode, enable.value, speed, direction.value]
    return self.set_generic_status(MksCommands.SET_MODE0_COMMAND, [mode, enable, speed, direction])   

def restore_default_parameters(self):
    """
    Restores the default parameters. After restored the parameters, motor driver will reboot, and
    needs to calibrate the motor.

    Args:        
        can_id (int): The can id

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.        

    Note: This is the same as pressing the "Next" key, then power on the motor.
    """       
    return self.set_generic_status(MksCommands.RESTORE_DEFAULT_PARAMETERS_COMMAND)   
