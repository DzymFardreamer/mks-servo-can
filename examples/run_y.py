import can
import time
import logging

from mks_servo_can import MksServo

# Stock slcan firmware on Windows
bus = can.interface.Bus(interface="slcan", channel="COM3", bitrate=500000)
notifier = can.Notifier(bus, [])


def wait_for_motor_idle2(timeout=None):
    print("Speed:", end="", flush=True)
    start_time = time.perf_counter()
    while ((time.perf_counter() - start_time < timeout) if timeout else True) and servo.is_motor_running():
        print(servo.read_motor_speed(), end=" ", flush=True)
        time.sleep(0.1)  # Small sleep to prevent busy waiting
    return servo.is_motor_running()


def move_motor(absolute_position, timeout=None):
    print(f"\nMoving motor to absolute position {absolute_position}", flush=True)
    servo.run_motor_absolute_motion_by_axis(SPEED, ACCEL, absolute_position)
    is_motor_running = wait_for_motor_idle2(timeout)
    value = servo.read_encoder_value_addition()
    error = absolute_position - value
    print(f"\nMovement at {absolute_position} with error {error}, {is_motor_running}", flush=True)


servo = MksServo(bus, notifier, 1)

print(servo.emergency_stop_motor())

print("Set subdivisions", 255)
print(servo.set_subdivisions(255))
print("Set work mode", MksServo.WorkMode.SrClose)
print(servo.set_work_mode(MksServo.WorkMode.SrClose))

print("Set working current", 2000)
print(servo.set_working_current(2000))
print("Set current axis to zero")
print(servo.set_current_axis_to_zero())
# print("Calibrate encoder")
# print(servo.b_calibrate_encoder())

print("Go home")
print(servo.set_home(MksServo.EndStopLevel.Low, MksServo.Direction.CW, 200, MksServo.Enable.Disable))
# print(servo.b_go_home())

print("Position")
print(servo.read_encoder_value_addition())

print("MOVING")
print(servo.run_motor_relative_motion_by_pulses(MksServo.Direction.CCW, 400, 1, 15000))
print(servo.wait_for_motor_idle())

print("Position 2")
print(servo.read_encoder_value_addition())
print(servo.run_motor_relative_motion_by_pulses(MksServo.Direction.CCW, 400, 1, 30000))
print(servo.wait_for_motor_idle())

print("Position 3")
print(servo.read_encoder_value_addition())
print(servo.run_motor_relative_motion_by_pulses(MksServo.Direction.CCW, 400, 1, 30000))
print(servo.wait_for_motor_idle(10))

print("Position 4")
print(servo.read_encoder_value_addition())

try:
    while True:
        move_motor(0x4000 * 2)
        move_motor(0)
except KeyboardInterrupt:
    pass

notifier.stop()
bus.shutdown()
