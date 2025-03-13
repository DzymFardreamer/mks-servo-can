import can
import time
import logging

from enum import Enum
from .mks_enums import Enable, SuccessStatus, MksCommands


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
    from .can_commands import (
        read_encoder_value_carry,
        read_encoder_value_addition,
        read_raw_encoder_value_addition,
        read_motor_speed,
        read_num_pulses_received,
        read_io_port_status,
        read_motor_shaft_angle_error,
        read_en_pins_status,
        read_go_back_to_zero_status_when_power_on,
        release_motor_shaft_locked_protection_state,
        read_motor_shaft_protection_state,
    )

    from .can_motor import (
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
        _validate_axis,
        query_motor_status,
        enable_motor,
        emergency_stop_motor,
        run_motor_in_speed_mode,
        stop_motor_in_speed_mode,
        save_clean_in_speed_mode,
        is_motor_running,
        wait_for_motor_idle,
        run_motor_relative_motion_by_pulses,
        run_motor_absolute_motion_by_pulses,
        run_motor_relative_motion_by_axis,
        run_motor_absolute_motion_by_axis,
        stop_motor_relative_motion_by_pulses,
        stop_motor_absolute_motion_by_pulses,
        stop_motor_relative_motion_by_axis,
        stop_motor_absolute_motion_by_axis,
    )
    from .can_set import (
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
        restore_default_parameters,
    )

    from .mks_enums import (
        Direction,
        Enable,
        SuccessStatus,
        LockedRotor,
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
        MotorStatus,
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
    MAX_CALIBRATION_TIME = 30
    MAX_HOMING_TIME = 20

    _calibration_status = CalibrationResult.Unknown
    _homing_status = GoHomeResult.Unknown
    _motor_run_status = RunMotorResult.RunComplete

    def __init__(self, bus, notifier, id):
        """Inits MksServo with the CAN bus and servo ID.

        Args:
            bus (can.interface.Bus): The CAN bus instance to be used.
            can_id (int): The CAN ID for this servo.
        """

        def monitor_incomming_messages(message):
            try:
                if message.arbitration_id == self.can_id:
                    self.check_msg_crc(message)
                    op_code = MksCommands(message.data[0])
                    if op_code == MksCommands.MOTOR_CALIBRATION_COMMAND and len(message.data) == self.GENERIC_RESPONSE_LENGTH:
                        status_int = int.from_bytes(message.data[1:2], byteorder="big")
                        try:
                            self._calibration_status = self.CalibrationResult(status_int)
                        except ValueError:
                            logging.warning(f"No enum member with value {status_int}")
                    elif (
                        op_code
                        in [
                            MksCommands.RUN_MOTOR_RELATIVE_MOTION_BY_PULSES_COMMAND,
                            MksCommands.RUN_MOTOR_ABSOLUTE_MOTION_BY_PULSES_COMMAND,
                            MksCommands.RUN_MOTOR_RELATIVE_MOTION_BY_AXIS_COMMAND,
                            MksCommands.RUN_MOTOR_ABSOLUTE_MOTION_BY_AXIS_COMMAND,
                            MksCommands.RUN_MOTOR_SPEED_MODE_COMMAND,
                        ]
                        and len(message.data) == self.GENERIC_RESPONSE_LENGTH
                    ):
                        status_int = int.from_bytes(message.data[1:2], byteorder="big")
                        try:
                            self._motor_run_status = self.RunMotorResult(status_int)
                        except ValueError:
                            logging.warning(f"No enum member with value {status_int}")
                    elif op_code == MksCommands.GO_HOME_COMMAND and len(message.data) == self.GENERIC_RESPONSE_LENGTH:
                        status_int = int.from_bytes(message.data[1:2], byteorder="big")
                        try:
                            self._homing_status = self.GoHomeResult(status_int)
                            print("self._homing_status", self._homing_status)
                        except ValueError:
                            logging.warning(f"No enum member with value {status_int}")
                    elif op_code == MksCommands.QUERY_MOTOR_STATUS_COMMAND:
                        # a = 1
                        pass
                    elif op_code in [
                        MksCommands.READ_ENCODED_VALUE_ADDITION,
                        MksCommands.READ_ENCODER_VALUE_CARRY,
                        MksCommands.READ_RAW_ENCODED_VALUE_ADDITION,
                        MksCommands.READ_NUM_PULSES_RECEIVED,
                        MksCommands.READ_IO_PORT_STATUS,
                        MksCommands.READ_MOTOR_SHAFT_ANGLE_ERROR,
                        MksCommands.READ_EN_PINS_STATUS,
                        MksCommands.READ_GO_BACK_TO_ZERO_STATUS_WHEN_POWER_ON,
                        MksCommands.RELEASE_MOTOR_SHAFT_LOCKED_PROTECTION_STATE,
                        MksCommands.READ_MOTOR_SHAFT_PROTECTION_STATE,
                    ]:
                        # a = 1
                        pass
                    elif op_code == MksCommands.READ_MOTOR_SPEED:
                        # speed = int.from_bytes(message.data[1:3], byteorder="big", signed=True)
                        # print("???", op_code, speed, "!!!")
                        pass
                    elif (
                        op_code
                        in [  # All set_generic_status() commands
                            MksCommands.ENABLE_MOTOR_COMMAND,
                            MksCommands.EMERGENCY_STOP_COMMAND,
                            MksCommands.SAVE_CLEAN_IN_SPEED_MODE_COMMAND,
                            MksCommands.SET_WORK_MODE_COMMAND,
                            MksCommands.SET_WORKING_CURRENT_COMMAND,
                            MksCommands.SET_HOLDING_CURRENT_COMMAND,
                            MksCommands.SET_SUBDIVISIONS_COMMAND,
                            MksCommands.SET_EN_PIN_CONFIG_COMMAND,
                            MksCommands.SET_MOTOR_ROTATION_DIRECTION,
                            MksCommands.SET_AUTO_TURN_OFF_SCREEN_COMMAND,
                            MksCommands.SET_MOTOR_SHAFT_LOCKED_ROTOR_PROTECTION_COMMAND,
                            MksCommands.SET_SUBDIVISION_INTERPOLATION_COMMAND,
                            MksCommands.SET_CAN_BITRATE_COMMAND,
                            MksCommands.SET_CAN_ID_COMMAND,
                            MksCommands.SET_SLAVE_RESPOND_ACTIVE_COMMAND,
                            MksCommands.SET_KEY_LOCK_ENABLE_COMMAND,
                            MksCommands.SET_GROUP_ID_COMMAND,
                            MksCommands.SET_HOME_COMMAND,
                            MksCommands.SET_CURRENT_AXIS_TO_ZERO_COMMAND,
                            MksCommands.SET_LIMIT_PORT_REMAP_COMMAND,
                            MksCommands.SET_MODE0_COMMAND,
                            MksCommands.RESTORE_DEFAULT_PARAMETERS_COMMAND,
                        ]
                        and len(message.data) == self.GENERIC_RESPONSE_LENGTH
                    ):
                        # status_int = int.from_bytes(message.data[1:2], byteorder="big")
                        # print("???", op_code, SuccessStatus(status_int), "!!!", flush=True)
                        pass
                    else:
                        print("message.data:", message.data)
                        print("op_code:", op_code)
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

    def set_generic(self, op_code: MksCommands, response_length, data=[]):
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
                        if message.data[0] != op_code:
                            logging.error(f"Unexpected opcode.")
                            logging.error(f"op_code:0x{op_code:X}")
                            logging.error(f"message.data[0]:0x{int(message.data[0]):X}")
                            logging.error(f"message.data:{message.data}")
                            logging.error(message)
                        if len(message.data) != response_length:
                            logging.error(f"Unexpected response length.")
                            logging.error(f"len(message.data):{len(message.data)}")
                            logging.error(f"response_length:{response_length}")
                            logging.error(f"message.data:{message.data}")
                            logging.error(message)
                        status = message.data
                except InvalidCRCError as e:
                    logging.error(f"CRC check failed for the message: {e}")

        try:
            self.notifier.add_listener(receive_message)
            self.bus.send(msg)
        except can.CanError as e:
            raise CanMessageError(f"Error sending message: {e}")

        # Wait for response (with a timeout)
        start_time = time.perf_counter()
        while (time.perf_counter() - start_time < self.timeout) and status is None:
            time.sleep(0.1)  # Small sleep to prevent busy waiting
        self.notifier.remove_listener(receive_message)

        return status

    def set_generic_status(self, op_code: MksCommands, data=[]) -> SuccessStatus | None:
        """Sends a generic status command and processes the response.

        Args:
            op_code (int): Operation code of the command.
            data (list of bytes, optional): Additional data for the command. Defaults to an empty list.

        Returns:
            dict: Modified result dictionary with 'status' key, None on error.
        """
        tmp = self.set_generic(op_code, MksServo.GENERIC_RESPONSE_LENGTH, data)
        if tmp is None:
            return None
        status_int = int.from_bytes(tmp[1:2], byteorder="big")

        try:
            return SuccessStatus(status_int)
        except ValueError:
            raise InvalidResponseError(f"No enum member with value {status_int}")

    def specialized_state(self, op_code: MksCommands, status_enum, status_enum_exception, data=None):
        tmp = self.set_generic(op_code, self.GENERIC_RESPONSE_LENGTH, [op_code.value] if data is None else data)
        if tmp is None:
            return None
        status_int = int.from_bytes(tmp[1:2], byteorder="big")
        try:
            return status_enum(status_int)
        except ValueError:
            raise status_enum_exception(f"No enum member with value {status_int}")
