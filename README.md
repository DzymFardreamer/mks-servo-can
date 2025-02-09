# MKS-Servo CAN Interface Library

## Description

This Python library provides an easy-to-use interface for communicating with MKS-Servo57D, MKS-Servo42D devices using the CAN protocol. It's built on top of the python-can library, offering a simplified way to send and receive CAN messages to control and monitor MKS-Servo devices.

## Features
- Easy connection to MKS-Servo devices via CAN.
- Send commands and receive responses from the device.
- Automatic handling of CAN message formatting.
- Error checking and handling for reliable communication.

## Installation
- To install this library, you can use pip: (Not yet)

```bash
pip install mks-servo-can
```

- To install this library from the local repository:

```bash
cd mks-servo-can
pip install .
```

## Requirements
- Python 3.x
- python-can library

# Quick Start
Here's a simple example `simple.py` of how to use this library:

```python
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
```

# Documentation
For more detailed documentation, visit [html/mks-servo-can/index.html].

# Contributing
Contributions to this library are welcome. Please read [CONTRIBUTING.md] for details on our code of conduct, and the process for submitting pull requests.

# License
This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the [LICENSE.md] file for details.

# Acknowledgments
Thanks to the python-can team for their excellent CAN interface library.
Special thanks to everyone who contributed to making this library.
