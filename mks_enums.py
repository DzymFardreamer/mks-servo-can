from enum import Enum

class MksCommands(Enum):
    READ_ENCODER_VALUE_CARRY = 0x30
    READ_ENCODED_VALUE_ADDITION = 0x31
    READ_MOTOR_SPEED = 0x32
    READ_NUM_PULSES_RECEIVED = 0x33
    READ_IO_PORT_STATUS = 0x34
    READ_MOTOR_SHAFT_ANGLE_ERROR = 0x39
    READ_EN_PINS_STATUS = 0x3A
    READ_GO_BACK_TO_ZERO_STATUS_WHEN_POWER_ON = 0x3B
    RELEASE_MOTOR_SHAFT_LOCKED_PROTECTION_STATE = 0x3D
    READ_MOTOR_SHAFT_PROTECTION_STATE = 0x3E
    QUERY_MOTOR_STATUS_COMMAND = 0xF1
    ENABLE_MOTOR_COMMAND = 0xF3
    EMERGENCY_STOP_COMMAND = 0xF7
    RUN_MOTOR_SPEED_MODE_COMMAND = 0xF6
    SAVE_CLEAN_IN_SPEED_MODE_COMMAND = 0xFF
    RUN_MOTOR_RELATIVE_MOTION_BY_PULSES_COMMAND = 0xFD
    RUN_MOTOR_ABSOLUTE_MOTION_BY_PULSES_COMMAND = 0xFE
    RUN_MOTOR_RELATIVE_MOTION_BY_AXIS_COMMAND = 0xF4
    RUN_MOTOR_ABSOLUTE_MOTION_BY_AXIS_COMMAND = 0xF5    


class Direction(Enum):
    CW = 1  # Clockwise
    CCW = 2  # Counter-Clockwise

class Enable(Enum):
    Disable = 0
    Enable = 1

class EnableStatus(Enum):
    Disabled = 0
    Enabled = 1    

class SuccessStatus(Enum):
    Fail = 0
    Success = 1    

class GoBackToZeroStatus(Enum):
    GoingToZero = 0
    GoBackToZeroSuccess = 1
    GoBackToZeroFail = 2

class StatusCommand8(Enum):
    ReleaseFails = 0
    ReleaseSuccess = 1

class StatusCommand9(Enum):
    NoProtected = 0,
    Protected = 1

class CalibrationResult(Enum):
    Unkown = 500    
    Calibrating = 0
    CalibratedSuccess = 1
    CalibratingFail = 2

class WorkMode(Enum):
    CrOpen = 0
    CrClose = 1
    CrvFoc = 2
    SrOpen = 3
    SrClose = 4
    SrvFoc = 5

class HoldingStrength(Enum):
    TEN_PERCENT = 0    
    TWENTLY_PERCENT = 1
    THIRTY_PERCENT = 2
    FOURTY_PERCENT = 3
    FIFTHTY_PERCENT = 4
    SIXTY_PERCENT = 5
    SEVENTY_PERCENT = 6
    EIGHTY_PERCENT = 7
    NIGHTY_PERCENT = 8

class EnPinEnable(Enum):
    ActiveLow = 0,
    ActiveHigh = 1
    ActiveAlways = 2

class CanBitrate(Enum):
    Rate125K = 0
    Rate250K = 1
    Rate500K = 2
    Rate1M = 3

class EndStopLevel(Enum):
    Low = 0
    High = 1

class GoHomeResult(Enum):
    Fail = 0
    Start = 1
    Success = 2

class Mode0(Enum):
    Disable = 0
    DirMode = 1
    NearMode = 2

class SaveCleanState(Enum):
    Save = 0xC8
    Clean = 0xCA

class RunMotorResult(Enum):
    RunFail = 0
    RunStarting = 1
    RunComplete = 2
    RunEndLimitStoped = 3

class MotorStatus(Enum):
    Fail = 0
    MotorStop = 1
    MotorSpeedUp = 2
    MotorSpeedDown = 3
    MotorFullSpeed = 4
    MotorHoming = 5
    MotorIsCalibrating = 6

class MotorShaftProtectionStatus(Enum):
    Protected = 1
    NotProtected = 0