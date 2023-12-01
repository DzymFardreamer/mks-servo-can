from enum import Enum


class Direction(Enum):
    CW = 1  # Clockwise
    CCW = 2  # Counter-Clockwise

class Enable(Enum):
    Disabled = 0
    Enabled = 1

class SuccessStatus(Enum):
    Fail = 0
    Success = 1    

class StatusCommand7:
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
    Calibrating = 0,
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
    