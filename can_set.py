
import can
import time
from mks_servo import MksServo
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

# TODO: It is a continuous call until result is 1 or 2?
def CalibrateEncoder(self):
    rslt = self.SetGeneric(0x80, 0x00)
    try:
        rslt.status = CalibrationResult(rslt.status)
    except ValueError:
        print(f"No enum member with value {rslt.status}")     
        return None                   
    return rslt    
MksServo = CalibrateEncoder(MksServo)

def SetWorkMode(self, mode: WorkMode):
    return self.SetGenericStatus(0x82, mode)
MksServo = SetWorkMode(MksServo)

def SetWorkingCurrent(self, current):
    if current < 0 or current > 5200:
        print("Invalid current")
        return None    

    op_code = 0x83
    response_length = 3

    msg = self.create_can_msg(self.can_id, [op_code, (current >> 8) & 0xFF, current & 0xFF])

    try:        
        self.bus.send(msg)
    except can.CanError:
        print("Error al enviar mensaje")
        return None

    # Wait for the response
    start_time = time.time()
    while True:
        if time.time() - start_time > self.timeout:
            print("self.timeout")
            return None

        message = self.bus.recv(0.1) 
        if message:
            if self.check_msg_crc(message):
                if message.arbitration_id == self.can_id:
                    if message.data[0] == op_code and len(message.data) == response_length:
                        status = int.from_bytes(message.data[1:2], byteorder='big')                        
                        try:
                            status = SuccessStatus(status)
                        except ValueError:
                            print(f"No enum member with value {status}")     
                            return None                   
                        return {'status': status}
                    else:
                        print("Unexpected data length")
                        return None
            else:
                print("Invalid message CRC") 
MksServo = SetWorkingCurrent(MksServo)

def SetHoldingCurrent(self, strength: HoldingStrength):
    return self.SetGenericStatus(0x9B, strength)    
MksServo = SetHoldingCurrent(MksServo)

def SetSubDivision(self, mstep):
    return self.SetGenericStatus(0x84, mstep)    
MksServo = SetSubDivision(MksServo)

def SetEnPinConfig(self, enable: EnPinEnable):
    return self.SetGenericStatus(0x85, enable)     
MksServo = SetEnPinConfig(MksServo)

def SetMotorRototationDirection(self, direction: Direction):
    return self.SetGenericStatus(0x86, direction)
MksServo = SetMotorRototationDirection(MksServo)

def SetAutoTurnOffScreen(self, enable: Enable):
    return self.SetGenericStatus(0x87, enable)
MksServo = SetAutoTurnOffScreen(MksServo)

def SetMotorShaftLockedRotorProtection(self, enable: Enable):
    return self.SetGenericStatus(0x88, enable)
MksServo = SetAutoTurnOffScreen(MksServo)

def SetSubDivisionInterpolation(self, enable: Enable):
    return self.SetGenericStatus(0x89, enable)
MksServo = SetSubDivisionInterpolation(MksServo)

def SetCanBitrate(self, bitrate: CanBitrate):
    return self.SetGenericStatus(0x8A, bitrate)
MksServo = SetCanBitrate(MksServo)

def SetCanId(self, can_id):
    return self.SetGenericStatus(0x8B, [(can_id >> 8) & 0xF, can_id & 0xFF])
MksServo = SetCanId(MksServo)

def SetSlaveRespondActive(self):
    print ("Not implemented")
MksServo = SetSlaveRespondActive(MksServo)

def SetKeyLockEnable(self, enable: Enable):
    return self.SetGenericStatus(0x8F, enable)
MksServo = SetCanBitrate(MksServo)

def SetGroupId(self, group_id):
    return self.SetGenericStatus(0x8D, [(group_id >> 8) & 0xF, group_id & 0xFF])
MksServo = SetCanId(MksServo)

def SetHome(self, homeTrig : EndStopLevel, homeDir: Direction, homeSpeed, endLimit: Enable):
    return self.SetGenericStatus(0x90, [homeTrig, homeDir, (homeSpeed >> 8) & 0xF, homeSpeed & 0xFF, endLimit])
MksServo = SetHome(MksServo)

def GoHome(self):
    rslt = self.SetGeneric(0x91)
    try:
        rslt.status = GoHomeResult(rslt.status)
    except ValueError:
        print(f"No enum member with value {rslt.status}")     
        return None                   
    return rslt    
MksServo = GoHome(MksServo)

def SetCurrentAxisToZero(self):
    return self.SetGenericStatus(0x92)   
MksServo = GoHome(MksServo)

def SetLimitPortRemap(self, enable: Enable):
    return self.SetGenericStatus(0x9E, enable)   
MksServo = GoHome(MksServo)    

def SetMode0(self, mode : Mode0, enable : Enable, speed, direction: Direction):
    cmd = [mode, enable, speed, direction]
    return self.SetGenericStatus(0x3F, [mode, enable, speed, direction])   
MksServo = SetMode0(MksServo)    

def RestoreDefaultParameters(self):
    return self.SetGenericStatus(0x3F)   
MksServo = RestoreDefaultParameters(MksServo)    