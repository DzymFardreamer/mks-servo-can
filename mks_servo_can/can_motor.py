import time

from .mks_enums import (
    Direction,
    Enable,
    SaveCleanState,
    RunMotorResult,
    StopMotorResult,
    MotorStatus,
    MksCommands,
)

# constants
MAX_SPEED = 3000
MAX_ACCELERATION = 255
MAX_PULSES = 0xFFFFFF
MAX_AXIS = +8388607  # 0x7FFFFF
MIN_AXIS = -8388608  # 0x800000  # ??? -8388607 ???


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


class invalid_axis_error(Exception):
    """Exception raised for invalid axis coordinate."""

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
        raise invalid_pulses_error(f"Pulses must be between 0 and {MAX_PULSES}")


def _validate_axis(self, axis):
    if axis < MIN_AXIS or axis > MAX_AXIS:
        raise invalid_axis_error(f"Must be between {MIN_AXIS} and {MAX_AXIS}")


def query_motor_status(self):
    """
    Query the motor status

    Returns:
        MotorStatus: The motor process status.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    return self.specialized_state(MksCommands.QUERY_MOTOR_STATUS_COMMAND, MotorStatus, motor_status_error)


def enable_motor(self, enable: Enable):
    return self.set_generic_status(MksCommands.ENABLE_MOTOR_COMMAND, enable)


def emergency_stop_motor(self):
    """
    Runs the emergency motor stop

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    return self.set_generic_status(MksCommands.EMERGENCY_STOP_COMMAND)


def run_motor_in_speed_mode(self, direction: Direction, speed, acceleration):
    """
    Sets the speed mode, where the motor can be run with a fixed acceleration and speed.

    Args:
        direction (Direction): The direction of the motor, CCW or CW.
        speed (int): The speed in the range of 0 to 3000 RPMs.
        acceleration (int): The acceleration in the range of 0 to 255.

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    self._validate_direction(direction)
    self._validate_speed(speed)
    self._validate_acceleration(acceleration)

    direction_value = 0x80 if direction == Direction.CW else 0

    cmd = [direction_value + ((speed >> 8) & 0b1111), speed & 0xFF, acceleration]
    return self.set_generic_status(MksCommands.RUN_MOTOR_SPEED_MODE_COMMAND, cmd)


def stop_motor_in_speed_mode(self, acceleration):
    return self.specialized_state(MksCommands.RUN_MOTOR_SPEED_MODE_COMMAND, StopMotorResult, motor_status_error, [0, 0, acceleration])


def save_clean_in_speed_mode(self, state: SaveCleanState):
    """
    Sets the save/clean parameter state in speed mode

    Args:
        state (SaveCleanState): The save/clean paramete state

    Returns:
        SuccessStatus: The success result of the command.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    return self.set_generic_status(MksCommands.SAVE_CLEAN_IN_SPEED_MODE_COMMAND)


def is_motor_running(self):
    """
    Returns the current running state of the motor
    Returns:
        boolean: The running state of the motor.
    """
    return self.query_motor_status() != MotorStatus.MotorStop


def wait_for_motor_idle(self, timeout=15):
    """
    Waits until the motor stops running or the timeout time is meet.

    Args:
        timeout (double): Maximum number of seconds to wait for the motor to stop, 0 - without waits, None - wait until the motor stops running.

    Returns:
        boolean: The running state of the motor at the end of this method.

    Raises:
        can.CanError: If there is an error in sending the CAN message.
    """
    start_time = time.perf_counter()
    while ((time.perf_counter() - start_time < timeout) if timeout else True) and self.is_motor_running():
        time.sleep(0.1)  # Small sleep to prevent busy waiting
    return self.is_motor_running()


def run_motor_relative_motion_by_pulses(self, direction: Direction, speed, acceleration, pulses):
    """
    The motor runs to the relative position with the set acceleration and speed.

    Args:
        direction (Direction): The direction of the motor, CCW or CW.
        speed (int): The speed in the range of 0 to 3000 RPMs.
        acceleration (int): The acceleration in the range of 0 to 255.
        pulses (int): The motor run steps, the value range is 0 to 0xFFFFFF.

    Returns:
        int: If successful, returns the status of the motor, at the end of the command execution.
        None: If there's an error in sending the message, a self.timeout occurs, or the response is
        invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.

    Note: If the motor is rotating more than 1000 RPM, it is not a good idea to stop the motor inmediately.
    """
    if self.is_motor_running():
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
    tmp = self.set_generic(MksCommands.RUN_MOTOR_RELATIVE_MOTION_BY_PULSES_COMMAND, self.GENERIC_RESPONSE_LENGTH, cmd)
    if tmp is None:
        return None
    status_int = int.from_bytes(tmp[1:2], byteorder="big")
    try:
        return RunMotorResult(status_int)
    except ValueError:
        raise motor_status_error(f"No enum member with value {status_int}")


def stop_motor_relative_motion_by_pulses(self, acceleration):
    return self.specialized_state(MksCommands.RUN_MOTOR_RELATIVE_MOTION_BY_PULSES_COMMAND, StopMotorResult, motor_status_error, [0, 0, acceleration, 0, 0, 0])


def run_motor_absolute_motion_by_pulses(self, speed, acceleration, absolute_pulses):
    """
    The motor runs to the specified position with the set acceleration and speed.

    Args:
        speed (int): The speed in the range of 0 to 3000 RPMs.
        acceleration (int): The acceleration in the range of 0 to 255.
        absolute_pulses (int): The absolute pulses, the value range is -8388607 to +8388607.

    Returns:
        int: If successful, returns the status of the motor, at the end of the command execution.
        None: If there's an error in sending the message, a self.timeout occurs, or the response is
    invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.

    Note: If the motor is rotating more than 1000 RPM, it is not a good idea to stop the motor inmediately.
    """
    if self.is_motor_running():
        raise motor_already_running_error("")
    self._validate_speed(speed)
    self._validate_axis(absolute_pulses)

    cmd = [
        (speed >> 8),
        speed & 0xFF,
        acceleration,
        (absolute_pulses >> 16) & 0xFF,
        (absolute_pulses >> 8) & 0xFF,
        (absolute_pulses >> 0) & 0xFF,
    ]
    tmp = self.set_generic(MksCommands.RUN_MOTOR_ABSOLUTE_MOTION_BY_PULSES_COMMAND, self.GENERIC_RESPONSE_LENGTH, cmd)
    if tmp is None:
        return None
    status_int = int.from_bytes(tmp[1:2], byteorder="big")
    try:
        return RunMotorResult(status_int)
    except ValueError:
        raise motor_status_error(f"No enum member with value {status_int}")


def stop_motor_absolute_motion_by_pulses(self, acceleration):
    return self.specialized_state(MksCommands.RUN_MOTOR_ABSOLUTE_MOTION_BY_PULSES_COMMAND, StopMotorResult, motor_status_error, [0, 0, acceleration, 0, 0, 0])


def run_motor_relative_motion_by_axis(self, speed, acceleration, relative_axis):
    """
    The motor runs relative to the axis with the set acceleration and speed. The axis is the encoder value in
    addition mode. It can be read using read_encoder_value_addition method.

    Args:
        speed (int): The speed in the range of 0 to 3000 RPMs.
        acceleration (int): The acceleration in the range of 0 to 255.
        relative_axis (int): The relative axis, the value range is -8388607 to +8388607.

    Returns:
        int: If successful, returns the status of the motor, at the end of the command execution.
        None: If there's an error in sending the message, a self.timeout occurs, or the response is
    invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.

    Note: In this mode, the axis error is about +-15. It is suggested running with 64 subdivisions.
    Note: If the motor is rotating more than 1000 RPM, it is not a good idea to stop the motor inmediately.
    """
    if self.is_motor_running():
        raise motor_already_running_error("")
    self._validate_speed(speed)
    self._validate_acceleration(acceleration)
    self._validate_axis(relative_axis)

    # TODO: Should we add a check to avoid stopping the motor inmediately when running at more than 1000 RPMs?
    cmd = [
        ((speed >> 8) & 0b1111),
        speed & 0xFF,
        acceleration,
        (relative_axis >> 16) & 0xFF,
        (relative_axis >> 8) & 0xFF,
        (relative_axis >> 0) & 0xFF,
    ]
    tmp = self.set_generic(MksCommands.RUN_MOTOR_RELATIVE_MOTION_BY_AXIS_COMMAND, self.GENERIC_RESPONSE_LENGTH, cmd)
    if tmp is None:
        return None
    status_int = int.from_bytes(tmp[1:2], byteorder="big")
    try:
        return RunMotorResult(status_int)
    except ValueError:
        raise motor_status_error(f"No enum member with value {status_int}")


def stop_motor_relative_motion_by_axis(self, acceleration):
    return self.specialized_state(MksCommands.RUN_MOTOR_RELATIVE_MOTION_BY_AXIS_COMMAND, StopMotorResult, motor_status_error, [0, 0, acceleration, 0, 0, 0])


def run_motor_absolute_motion_by_axis(self, speed, acceleration, absolute_axis):
    """
    The motor runs to the specified axis with the set acceleration and speed. The axis is the encoder value in
    addition mode. It can be read using read_encoder_value_addition method.

    Args:
        speed (int): The speed in the range of 0 to 3000 RPMs.
        acceleration (int): The acceleration in the range of 0 to 255.
        absolute_axis (int): The relative axis, the value range is -8388607 to +8388607.

    Returns:
        int: If successful, returns the status of the motor, at the end of the command execution.
        None: If there's an error in sending the message, a self.timeout occurs, or the response is
    invalid.

    Raises:
        can.CanError: If there is an error in sending the CAN message.

    Note: In this mode, the axis error is about +-15. It is suggested running with 64 subdivisions.
    Note: If the motor is rotating more than 1000 RPM, it is not a good idea to stop the motor inmediately.
    """
    if self.is_motor_running():
        raise motor_already_running_error("")
    self._validate_speed(speed)
    self._validate_acceleration(acceleration)
    self._validate_axis(absolute_axis)

    # TODO: Should we add a check to avoid stopping the motor inmediately when running at more than 1000 RPMs?
    cmd = [
        ((speed >> 8) & 0b1111),
        speed & 0xFF,
        acceleration,
        (absolute_axis >> 16) & 0xFF,
        (absolute_axis >> 8) & 0xFF,
        (absolute_axis >> 0) & 0xFF,
    ]
    tmp = self.set_generic(MksCommands.RUN_MOTOR_ABSOLUTE_MOTION_BY_AXIS_COMMAND, self.GENERIC_RESPONSE_LENGTH, cmd)
    if tmp is None:
        return None
    status_int = int.from_bytes(tmp[1:2], byteorder="big")
    try:
        return RunMotorResult(status_int)
    except ValueError:
        raise motor_status_error(f"No enum member with value {status_int}")


def stop_motor_absolute_motion_by_axis(self, acceleration):
    return self.specialized_state(MksCommands.RUN_MOTOR_ABSOLUTE_MOTION_BY_AXIS_COMMAND, StopMotorResult, motor_status_error, [0, 0, acceleration, 0, 0, 0])
