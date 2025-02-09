import can

from mks_servo_can import MksServo

# Initialize the interface
bus = can.interface.Bus(interface="slcan", channel="COM3", bitrate=500000)
notifier = can.Notifier(bus, [])

# Connect to the servo, CAN ID 1
servo = MksServo(bus, notifier, 1)

# Send a command
print("Read encoder value addition")
print(servo.read_encoder_value_addition())
print("Read motor speed")
print(servo.read_motor_speed())

# Close the connection
notifier.stop()
bus.shutdown()
