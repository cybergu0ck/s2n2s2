from . import *
import serial
import time

PORT = "/dev/ttyS0"
BAUD_RATE = 115200
TIME_OUT = 1
if PI_MODE:
    global SERRIAL_OBJECT
    SERRIAL_OBJECT = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)


def configure_serial(SERRIAL_OBJECT):
    SERRIAL_OBJECT.write(b"AT+CMGF=1\r")  # Set the SMS message format to text mode
    user_command = SERRIAL_OBJECT.readline().decode().strip()  # Read the echoed command
    if DEV_MODE:
        print(f"\nuser command : {user_command}")

    response = SERRIAL_OBJECT.readline().decode().strip()  # Read the actual response
    if DEV_MODE:
        print(f"response : {response}\n")


def send_sms_text(recipient_phone_number, sms_message) -> bool:
    if is_valid_phone_number(recipient_phone_number):
        SERRIAL_OBJECT.write(f'AT+CMGS="{recipient_phone_number}"\r'.encode())
        user_command = SERRIAL_OBJECT.readline().decode().strip()
        if DEV_MODE:
            print(f"\nuser command : {user_command}")
        response = SERRIAL_OBJECT.readline().decode().strip()
        if DEV_MODE:
            print(f"response : {response}\n")

        SERRIAL_OBJECT.write(
            f"{sms_message}\x1A".encode()
        )  # \x1A is the ASCII code for Ctrl+Z
        user_command = SERRIAL_OBJECT.readline().decode().strip()
        if DEV_MODE:
            print(f"\nuser command : {user_command}")
        response = SERRIAL_OBJECT.readline().decode().strip()
        if DEV_MODE:
            print(f"response : {response}\n")

        time.sleep(5)
        return True
    else:
        return False
