

import can
import time
import logging
from enum import Enum

from mks_enums import Enable, SuccessStatus, MksCommands

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
    from can_commands import (
        read_encoder_value_carry,
        read_encoder_value_addition,
        read_motor_speed,
        read_num_pulses_received,
        read_io_port_status,
        read_motor_shaft_angle_error,
        read_en_pins_status,
        read_go_back_to_zero_status_when_power_on,
        release_motor_shaft_locked_protection_state,
        read_motor_shaft_protection_state
    )

    from can_motor import (
        MAX_SPEED,
        MAX_ACCELERATION,
        MAX_PULSES,
        invalid_direction_error,
        invalid_speed_error,
        invalid_aceleration_error,
        invalid_pulses_error,
        motor_status_error,
        _validate_direction,
        _validate_speed,
        _validate_acceleration,
        _validate_pulses,
        query_motor_status,
        enable_motor,
        emergency_stop_motor,
        run_motor_in_speed_mode,
        save_clean_in_speed_mode,
        is_motor_running,
        wait_for_motor_idle,        
        run_motor_relative_motion_by_pulses,
        run_motor_absolute_motion_by_pulses,
        run_motor_relative_motion_by_axis,
        run_motor_absolute_motion_by_axis
    )
    from can_set import (
        _validate_current,
        nb_calibrate_encoder,
        b_calibrate_encoder,
        wait_for_calibration,
        set_work_mode,
        set_working_current,
        set_holding_current,
        set_subdivisions,
        set_en_pin_config,
        set_motor_rotation_direction,
        set_auto_turn_off_screen,
        set_motor_shaft_locked_rotor_protection,
        set_subdivision_interpolation,
        set_can_bitrate,
        set_can_id,
        set_slave_respond_active,
        set_key_lock,
        set_group_id,
        set_home,
        nb_go_home,
        b_go_home,
        wait_for_go_home,
        set_current_axis_to_zero,
        set_limit_port_remap,
        set_mode0,
        restore_default_parameters
    )

    from mks_enums import (
        Direction,
        Enable,
        SuccessStatus,
        StatusCommand8,
        StatusCommand9,
        CalibrationResult,
        WorkMode,
        HoldingStrength,
        EnPinEnable,
        CanBitrate,
        EndStopLevel,
        GoHomeResult,
        Mode0,
        SaveCleanState,
        RunMotorResult,
        MotorStatus
    )

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
    MAX_CALIBRATION_TIME = 20
    MAX_HOMING_TIME = 20

    _calibration_status = CalibrationResult.Unkown
    _homing_status = GoHomeResult.Unkown
    _motor_run_status = RunMotorResult.RunComplete

    def __init__ (self, bus, notifier, id):
        """Inits MksServo with the CAN bus and servo ID.

        Args:
            bus (can.interface.Bus): The CAN bus instance to be used.
            can_id (int): The CAN ID for this servo.
        """     

        def monitor_incomming_messages(message):
            try:                                  
                if message.arbitration_id == self.can_id:
                    self.check_msg_crc(message)
                    if (message.data[0] == MksCommands.MOTOR_CALIBRATION_COMMAND.value and len(message.data) == self.GENERIC_RESPONSE_LENGTH):
                        status_int = int.from_bytes(message.data[1:2], byteorder='big')  
                        try:
                            self._calibration_status = self.CalibrationResult(status_int)                            
                        except ValueError:
                            logging.warning(f"No enum member with value {status_int}")    
                    elif (message.data[0] == MksCommands.RUN_MOTOR_RELATIVE_MOTION_BY_PULSES_COMMAND.value and len(message.data) == self.GENERIC_RESPONSE_LENGTH):
                        status_int = int.from_bytes(message.data[1:2], byteorder='big')  
                        try:
                            self._motor_run_status = self.RunMotorResult(status_int)                            
                        except ValueError:
                            logging.warning(f"No enum member with value {status_int}")      
                    elif (message.data[0] == MksCommands.RUN_MOTOR_ABSOLUTE_MOTION_BY_PULSES_COMMAND.value and len(message.data) == self.GENERIC_RESPONSE_LENGTH):
                        status_int = int.from_bytes(message.data[1:2], byteorder='big')  
                        try:
                            self._motor_run_status = self.RunMotorResult(status_int)                            
                        except ValueError:
                            logging.warning(f"No enum member with value {status_int}")  
                    elif (message.data[0] == MksCommands.RUN_MOTOR_RELATIVE_MOTION_BY_AXIS_COMMAND.value and len(message.data) == self.GENERIC_RESPONSE_LENGTH):
                        status_int = int.from_bytes(message.data[1:2], byteorder='big')  
                        try:
                            self._motor_run_status = self.RunMotorResult(status_int)                            
                        except ValueError:
                            logging.warning(f"No enum member with value {status_int}")                                                                                                                                      
                    elif (message.data[0] == MksCommands.RUN_MOTOR_ABSOLUTE_MOTION_BY_AXIS_COMMAND.value and len(message.data) == self.GENERIC_RESPONSE_LENGTH):
                        status_int = int.from_bytes(message.data[1:2], byteorder='big')  
                        try:
                            self._motor_run_status = self.RunMotorResult(status_int)                            
                        except ValueError:
                            logging.warning(f"No enum member with value {status_int}")                                                       
                    elif (message.data[0] == MksCommands.GO_HOME_COMMAND.value and len(message.data) == self.GENERIC_RESPONSE_LENGTH):
                        status_int = int.from_bytes(message.data[1:2], byteorder='big')  
                        try:
                            self._homing_status = self.GoHomeResult(status_int)                            
                        except ValueError:
                            logging.warning(f"No enum member with value {status_int}")                          
                    elif message.data[0] == MksCommands.QUERY_MOTOR_STATUS_COMMAND.value:
                        a = 1
                    elif message.data[0] == MksCommands.READ_ENCODED_VALUE_ADDITION.value:
                        a = 1                       
                    else:           
                        print(message, flush=True)                                       
            except InvalidCRCError:
                logging.error(f"CRC check failed for the message")                    
            return True
                   
        self.can_id = id
        self.bus = bus
        self.notifier = notifier
        self.timeout = MksServo.DEFAULT_TIMEOUT
        self.notifier.add_listener(monitor_incomming_messages)

    def _bool_to_int(self, value):
        """
        Checks if the input is a boolean. If yes, returns 1 for True and 0 for False.
        If the input is not a boolean, the value is returned.

        Args:
        - value: The value to be checked and converted.

        Returns:
        - int: 1 if value is True, 0 if value is False, value otherwise
        - str: A message if the value is not a boolean.
        """
        if isinstance(value, bool):
            return [1] if value else [0]
        else:
            return value

    
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
        
        can_message = can.Message(arbitration_id=self.can_id, data=write_data, is_extended_id=False)            
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
        if isinstance(op_code, Enum):
            op_code = op_code.value

        # Check if data is an integer and convert it to a list if it is
        if isinstance(data, int):
            data = [data]
        elif isinstance(data, bool):
            # Assuming _bool_to_int is a method that converts a boolean to an integer
            data = self._bool_to_int(data)
                    
        msg = self.create_can_msg([op_code] + data)
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
                        status = message.data                                                                
                except InvalidCRCError:
                    logging.error(f"CRC check failed for the message: {e}")            

        try:        
            self.notifier.add_listener(receive_message)
            self.bus.send(msg)
        except can.CanError as e:
            raise CanMessageError(f"Error sending message: {e}")            

        # Wait for response (with a timeout)
        start_time = time.perf_counter()
        while (time.perf_counter() - start_time < self.timeout) and status == None:
            time.sleep(0.1)  # Small sleep to prevent busy waiting
        self.notifier.remove_listener(receive_message)

        return status
                      
    def set_generic_status(self, op_code, data = []):
        """Sends a generic status command and processes the response.

        Args:
            op_code (int): Operation code of the command.
            data (list of bytes, optional): Additional data for the command. Defaults to an empty list.

        Returns:
            dict: Modified result dictionary with 'status' key, None on error.
        """        
        tmp = self.set_generic(op_code, MksServo.GENERIC_RESPONSE_LENGTH, data)
        if not tmp == None:
            status_int = int.from_bytes(tmp[1:2], byteorder='big')  

            try:            
                return SuccessStatus(status_int)
            except ValueError:
                raise InvalidResponseError(f"No enum member with value {status_int}")
                
        return None
    
    def specialized_state(self, op_code, status_enum, status_enum_exception):
        tmp = self.set_generic(op_code, self.GENERIC_RESPONSE_LENGTH, [op_code.value])  
        status_int = int.from_bytes(tmp[1:2], byteorder='big')  
        try:
            return status_enum(status_int)
        except ValueError:
            raise status_enum_exception(f"No enum member with value {status_int}")                     
        