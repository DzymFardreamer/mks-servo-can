import can
import time
import logging

from mks_servo_can import MksServo

# Stock slcan firmware on Windows
bus = can.interface.Bus(interface="slcan", channel="COM3", bitrate=500000)
notifier = can.Notifier(bus, [])


def wait_for_motor_idle2(timeout):
    print("Speed:", end="", flush=True)
    start_time = time.perf_counter()
    while (time.perf_counter() - start_time < timeout) and servo.is_motor_running():
        print(servo.read_motor_speed(), end=" ", flush=True)
        time.sleep(0.1)  # Small sleep to prevent busy waiting
    return servo.is_motor_running()


# class ServoAxis(Enum):
#    ServoX = 0,
#    ServoY = 1
def move_motor(absolute_position):
    print(f"\nMoving motor to absolute position {absolute_position}", flush=True)
    print(servo.run_motor_absolute_motion_by_axis(600, 1, absolute_position), flush=True)
    wait_for_motor_idle2(30)
    value = servo.read_encoder_value_addition()
    error = absolute_position - value
    print(f"\nMovement at {absolute_position} with error {error}", flush=True)

    while False:
        status = servo.query_motor_status()
        # print(servo.read_encoder_value_carry())
        print(servo.read_encoder_value_addition())

        # Check if the status is MotorStop
        if status["status"] == MksServo.MotorStatus.MotorStop:
            print("Motor has stopped.", flush=True)
            break

        # Wait for 100 ms
        time.sleep(0.1)


servo = MksServo(bus, notifier, 1)

# if not servo.b_calibrate_encoder()['status'] == MksServo.CalibrationResult.CalibratedSuccess:
#   logging.error("Calibration failed")

print(servo.set_slave_respond_active(MksServo.Enable.Enable, MksServo.Enable.Enable))

try:
    print("emergency_stop_motor")
    print(servo.emergency_stop_motor())
except:
    pass

print(servo.set_work_mode(MksServo.WorkMode.SrvFoc))
print(servo.set_subdivisions(16))
print(servo.set_working_current(2000))
print(servo.set_current_axis_to_zero())

# print(servo.run_motor_relative_motion_by_pulses(MksServo.Direction.CW, 50, 1, 0x000A000))
# print(servo.run_motor_absolute_motion_by_pulses(400, 2, 0x0FA00))

move_motor(0x4000)
move_motor(-0x4000)
move_motor(0x4000)

# Test command 01:
print("---- 5.1.1 Read the encoder value (carry)----")
print(servo.read_encoder_value_carry())

print("---- 5.1.2 Read the encoder value (addition) ----")
print(servo.read_encoder_value_addition())

print("---- 5.1.3 Read the real-time speed of the motor ----")
print(servo.read_motor_speed())

print("---- 5.1.4 Read the number of pulses received ----")
print(servo.read_num_pulses_received())

print("---- 5.1.5 Read the IO Ports status ----")
print(servo.read_io_port_status())

print("---- 5.1.6 Read the error of the motor shaft angle ----")
print(servo.read_motor_shaft_angle_error())

print("---- 5.1.7 Read the En pins status ----")
print(servo.read_en_pins_status())

print("---- 5.1.8 Read the go back to zero status when power on ----")
print(servo.read_go_back_to_zero_status_when_power_on())

print("---- 5.1.9 Release the motor shaft locked-rotor protection state ----")
print(servo.release_motor_shaft_locked_protection_state())

print("---- 5.1.10 Read the motor shaft protection state ----")
print(servo.read_motor_shaft_protection_state())

# print("---- 5.2.1 Calibrate the encoder ----")
# print(servo.b_calibrate_encoder())

print("---- 5.2.2 Set the work mode ----")
print(servo.set_work_mode(MksServo.WorkMode.SrOpen))

print("---- 5.2.3 Set the working current ----")
print(servo.set_working_current(1000))

print("---- 5.2.4 Set the holding current percentage ----")
print(servo.set_holding_current(MksServo.HoldingStrength.FIFTHTY_PERCENT))

print("---- 5.2.5 Set subdivisions ----")
print(servo.set_subdivisions(4))

print("---- 5.2.6 Set the active of the En pin ----")
print(servo.set_en_pin_config(MksServo.EnPinEnable.ActiveHigh))

print("---- 5.2.7 Set the direction of motor rotation ----")
print(servo.set_motor_rotation_direction(MksServo.Direction.CW))

print("---- 5.2.8 Set auto turn off the screen function ----")
print(servo.set_auto_turn_off_screen(MksServo.Enable.Disable))

print("---- 5.2.9 Set the motor shaft locked-rotor protection function ----")
print(servo.set_motor_shaft_locked_rotor_protection(MksServo.Enable.Enable))

print("---- 5.2.10 Set the subdivision interpolation function ----")
print(servo.set_subdivision_interpolation(MksServo.Enable.Enable))

print("---- 5.2.11 Set the CAN bitRate ----")
print(servo.set_can_bitrate(MksServo.CanBitrate.Rate500K))

print("---- 5.2.12 Set the CAN ID  ----")
print(servo.set_can_id(1))

print("---- 5.2.13 Set the slave respond and active  ----")
print(servo.set_slave_respond_active(MksServo.Enable.Enable, MksServo.Enable.Enable))

print("---- 5.2.14 Set the key lock or unlock ----")
print(servo.set_key_lock(MksServo.Enable.Disable))

print("---- 5.2.15 Set the group ID  ----")
print(servo.set_group_id(0))

print("---- 5.3.1 Set the parameter of home ----")
print(servo.set_home(MksServo.EndStopLevel.High, MksServo.Direction.CW, 5, MksServo.Enable.Enable))

print("---- 5.3.2 Go home ----")
print(servo.nb_go_home())

print("---- 5.3.3 Set Current Axis to Zero ----")
print(servo.set_current_axis_to_zero())

print("---- 5.3.4 Set limit port remap ----")
print(servo.set_limit_port_remap(MksServo.Enable.Enable))

print("---- 5.4 Set the parameter of 0_mode ----")
print(servo.set_mode0(MksServo.Mode0.NearMode, MksServo.Enable.Enable, 2, MksServo.Direction.CW))

print("---- 5.5 Restore the default parameter ----")
print(servo.restore_default_parameters())


print("---- 6.2.1 Query the motor status ----")
print(servo.query_motor_status())

print("---- 6.2.2 Enable motor command ----")
print(servo.enable_motor(True))

print("---- 6.2.3 Emergency stop the motor ----")
print(servo.emergency_stop_motor())

print("---- 6.4.1 Speed mode command ----")
print(servo.run_motor_in_speed_mode(MksServo.Direction.CW, 320, 2))
print(servo.wait_for_motor_idle())

print("---- 6.4.3 Save/Clean the parameter in speed mode  ----")
print(servo.save_clean_in_speed_mode(MksServo.SaveCleanState.Clean))

print("---- 6.5.1 position mode1: relative motion by pulses ----")
print(servo.run_motor_relative_motion_by_pulses(MksServo.Direction.CW, 200, 1, 0x4000))
print(servo.wait_for_motor_idle())

print("---- 6.6.1 Position mode 2: absolute motion by pulses ----")
print(servo.run_motor_absolute_motion_by_pulses(400, 2, 0x4000))
print(servo.wait_for_motor_idle())

print("---- 6.7.1 Position mode 3: relative motion by axis ----")
print(servo.run_motor_relative_motion_by_axis(200, 1, 0x4000))
print(servo.wait_for_motor_idle())

print("---- 6.8.1 Position mode 4: Absolute motion by axis ----")
print(servo.run_motor_absolute_motion_by_axis(200, 1, -0x4000))
print(servo.query_motor_status())
print(servo.wait_for_motor_idle())
print(servo.query_motor_status())

try:
    while True:
        move_motor(0x4000 * 10)
        move_motor(0)
except KeyboardInterrupt:
    pass

notifier.stop()
bus.shutdown()
