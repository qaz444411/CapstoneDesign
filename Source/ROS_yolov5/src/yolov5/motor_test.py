from serial import Serial
import time

def create_command(steering, speed):
    STX = 0xEA
    ETX = 0x03

    # Calculate Length
    Length = 0x03

    # Set dummy values
    dummy1 = 0x00
    dummy2 = 0x00

    # Calculate Checksum
    Checksum = ((~(Length + steering + speed + dummy1 + dummy2)) & 0xFF) + 1
    #print(Checksum)

    # Create the command bytearray
    command = bytearray([STX, Length, steering, speed, dummy1, dummy2, Checksum, ETX])

    return command

ser = Serial('/dev/arduino', 115200, timeout=0.5)

# ser = Serial('/dev/ttyUSB0', 115200, timeout=0.5)



while True:
    try:
        # Steering 45, Speed 97, Delay 3 sec
        str_val = 0x2D
        spd_val = 0x61
        ser.write(create_command(str_val, spd_val))
        time.sleep(3)

        # Steering 135, Speed 99, Delay 3 sec
        str_val = 0x87
        spd_val = 0x63
        ser.write(create_command(str_val, spd_val))
        time.sleep(3)

    except KeyboardInterrupt:
        str_val = 0x5A
        ser.write(create_command(str_val, 0x00))
        break

ser.close()
