import can
import time
 
from can_commands import MksServo 

# Stock slcan firmware on Windows
bus = can.interface.Bus(bustype='slcan', channel='COM3', bitrate=500000)

servo = MksServo(bus, 1)

# Test command 01:
print ("---- Testing command 01 ----")
#print(read_encoder_value_carry())

print ("---- Testing command 02 ----")
#print(read_encoder_value_addition())

print ("---- Testing command 03 ----")
#print(read_motor_speed())

print ("---- Testing command 04 ----")
#print(read_num_pulses_recieved())

print ("---- Testing command 06 ----")
#print(read_io_port_status())

print ("---- Testing command 05 ----")
#print(read_motor_shaft_angle_error())

print ("---- Testing command 06 ----")
#print(read_en_pins_status())

print ("---- Testing command 07 ----")
#print(read_go_back_to_zero_status_when_power_on())

print ("---- Testing command 08 ----")
#print(release_motor_shaft_locked_protection_state())

print ("---- Testing command 09 ----")
#print(read_motor_shaft_protection_state())

print ("---- 6.2 Query the motor status ----")
print(servo.query_motor_status())

print ("---- 6.2 Enable motor command ----")
print(servo.enable_motor(True))

print ("---- 6.4 Speed mode command ----")
#print(run_motor_speed_mode(Direction.CW, 320, 2))

print ("---- 6.5 position mode1: relative motion by pulses ----")
print(servo.run_motor_relative_motion_by_pulses(MksServo.Direction.CW, 400, 2, 0x0FFA00))

# Llamar a la función
#value = read_io_port_status()
#if value is not None :
#    print("Value:", value)
#else:
#    print("No se recibió una respuesta válida")
    

bus.shutdown()
