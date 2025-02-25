import time

from .mks_enums import (
    MksCommands,
    MotorShaftProtectionStatus,
    SuccessStatus,
    GoBackToZeroStatus,
    EnableStatus,
    LockedRotor,
)


class motor_shaft_protection_status_error(Exception):
    """Exception raised for invalid motor shaft protection status."""

    pass


class success_status_error(Exception):
    """Exception raised for invalid motor shaft protection status."""

    pass


class go_back_to_zero_status_error(Exception):
    """Exception raised for invalid motor shaft protection status."""

    pass


class enable_status_error(Exception):
    """Exception raised for invalid motor shaft protection status."""

    pass


def read_encoder_value_carry(self):
    """
    Reads the encoder value

    Returns:
        dict or None: If successful, returns a dictionary with 'carry' and 'value' from the encoder.
    Returns None if there's an error in sending the message, a self.timeout occurs, or the response is
    invalid.

    Keyword Returns:
        <carry> int: The carry value of the encoder.
            When value is greather than 0x3FFF, carry += 1.
            When value is less than 0, carry -= 1

        <value> int: The current value of the encoder (range from 0 to 0x3FFF).

    Raises:
        can.CanError: If there is an error in sending the CAN message.

    Examples:
        if the current carry is 0 and value is 0x3FF0, after one turn CCW, the carry is 1 and value is 0x3FF0.
        if the current carry is 0 and value is 0x3FF0, after one turn CW, the carry is -1 and value is 0x3FF0.
    """
    op_code = MksCommands.READ_ENCODER_VALUE_CARRY
    response_length = 8

    data = self.set_generic(op_code, response_length, [op_code.value])

    if data:
        carry = int.from_bytes(data[1:5], byteorder="big", signed=True)
        value = int.from_bytes(data[5:7], byteorder="big", signed=True)
        return {"carry": carry, "value": value}

    return None


def read_encoder_value_addition(self):
    """
    Reads the encoder value in addition mode

    Returns:
        int: If successful, returns the current value of the encoder (range from 0 to +-0x7FFFFFFFFFFF).
        None: if there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.

    Examples:
        if the current value is 0x3FF0, after one turn CCW, the carry is 1 and value is 0x7FF0.
        if the current value is 0x3FF0, after one turn CW, the carry is -1 and value is -0x10.
    """
    op_code = MksCommands.READ_ENCODED_VALUE_ADDITION
    response_length = 8

    data = self.set_generic(op_code, response_length, [op_code.value])

    if data:
        return int.from_bytes(data[1:7], byteorder="big", signed=True)
    return None


def read_raw_encoder_value_addition(self):
    """
    Reads the encoder value in addition mode

    Returns:
        int: If successful, returns the current value of the encoder (range from 0 to +-0x7FFFFFFFFFFF).
        None: if there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.

    Examples:
        if the current value is 0x3FF0, after one turn CCW, the carry is 1 and value is 0x7FF0.
        if the current value is 0x3FF0, after one turn CW, the carry is -1 and value is -0x10.
    """
    op_code = MksCommands.READ_RAW_ENCODED_VALUE_ADDITION
    response_length = 8

    data = self.set_generic(op_code, response_length, [op_code])

    if data:
        return int.from_bytes(data[1:7], byteorder="big", signed=True)
    return None


def read_motor_speed(self):
    """
    Read the real-time speed of the motor (RPM).

    Returns:
        int: If successful, returns the current speed of the motor in RPM.
        None: if there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.

    Note:
        If it runs CCW, the speed is positive.
        If it runs CW, the speed is negative.
    """
    op_code = MksCommands.READ_MOTOR_SPEED
    response_length = 4

    data = self.set_generic(op_code, response_length, [op_code.value])

    # TODO: Raise an exception here  if there is a problem parsing the response
    if data:
        return int.from_bytes(data[1:3], byteorder="big", signed=True)
    return None


def read_num_pulses_received(self):
    """
    Reads the number of pulses received

    Returns:
        int: If successful, returns the number of pulses received.
        None: if there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    op_code = MksCommands.READ_NUM_PULSES_RECEIVED
    response_length = 6

    data = self.set_generic(op_code, response_length, [op_code.value])

    # TODO: Raise an exception here  if there is a problem parsing the response
    if data:
        return int.from_bytes(data[1:5], byteorder="big", signed=True)
    return None


def read_io_port_status(self):
    """
    Reads the IO Ports status

    Returns:
        int: If successful, returns the port status as Bit[0] is IN_1, Bit[1] is IN_2, Bit[2] is OUT_1, Bit[3] is OUT_2
        None: if there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    op_code = MksCommands.READ_IO_PORT_STATUS
    response_length = 3
    data = self.set_generic(op_code, response_length, [op_code.value])

    # TODO: Parse the response and return the data in a dictionary for each of the pins
    if data:
        return int.from_bytes(data[1:2], byteorder="big")
    return None


def read_motor_shaft_angle_error(self):
    """
    Reads the error on the motor shaft angle.

    The error is the difference between the angle you want to control minus the real-time angle of the motor.

    Returns:
        int: If successful, returns the error of the motor shaft angle.
        None: if there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.

    Note:
        0 to 51200 corresponds to 0 to 360º.

    Example:
        When the angle error is 1º, the return error is 51200/360 = 142.
    """
    op_code = MksCommands.READ_MOTOR_SHAFT_ANGLE_ERROR
    response_length = 6
    data = self.set_generic(op_code, response_length, [op_code.value])

    # TODO: Raise an exception here  if there is a problem parsing the response
    if data:
        return int.from_bytes(data[1:5], byteorder="big", signed=True)
    return None


def read_en_pins_status(self):
    """
    Reads the En pins status

    Returns:
        int: If successful, returns the enable pin status.
        None: if there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    return self.specialized_state(MksCommands.READ_EN_PINS_STATUS, EnableStatus, enable_status_error)


def read_go_back_to_zero_status_when_power_on(self):
    """
    Reads the go back to zero status when power on

    Returns:
        int: If successful, returns the go back to zero status.
        None: if there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    return self.specialized_state(
        MksCommands.READ_GO_BACK_TO_ZERO_STATUS_WHEN_POWER_ON,
        GoBackToZeroStatus,
        go_back_to_zero_status_error,
    )


def release_motor_shaft_locked_protection_state(self):
    """
    Release the motor shaft locked-rotor protection state.

    Returns:
        int: If successful, returns the release motor shaft locked protection state.
        None: if there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    return self.specialized_state(
        MksCommands.RELEASE_MOTOR_SHAFT_LOCKED_PROTECTION_STATE,
        LockedRotor,
        success_status_error,
    )


def read_motor_shaft_protection_state(self):
    """
    Read the motor shaft protection state.

    Returns:
        int: If successful, returns the motor shaft protection state.
        None: if there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    return self.specialized_state(
        MksCommands.READ_MOTOR_SHAFT_PROTECTION_STATE,
        MotorShaftProtectionStatus,
        motor_shaft_protection_status_error,
    )
