import can
import time
import logging

from mks_servo_can import MksServo

# Stock slcan firmware on Windows
bus = can.interface.Bus(interface="slcan", channel="COM3", bitrate=500000)
notifier = can.Notifier(bus, [])


def wait_for_motor_idle2(timeout):
    start_time = time.perf_counter()
    while (time.perf_counter() - start_time < timeout) and servo.is_motor_running():
        print(servo.read_motor_speed(), flush=True)
        time.sleep(0.1)  # Small sleep to prevent busy waiting
    return servo.is_motor_running()


def move_motor(absolute_position):
    print(f"Moving motor to absolute position {absolute_position}", flush=True)
    print(servo.run_motor_absolute_motion_by_axis(600, 0, absolute_position), flush=True)
    wait_for_motor_idle2(30)
    value = servo.read_encoder_value_addition()
    error = absolute_position - value
    print(f"Movement at {absolute_position} with error {error}")
    print(f"", flush=True)
    print()


servo = MksServo(bus, notifier, 1)

print(servo.emergency_stop_motor())
print(servo.set_work_mode(MksServo.WorkMode.SrvFoc))
print(servo.set_subdivisions(16))
print(servo.set_working_current(2000))
print(servo.set_current_axis_to_zero())

try:
    while True:
        move_motor(0x4000 * 10)
        move_motor(0)
except KeyboardInterrupt:
    pass

notifier.stop()
bus.shutdown()
