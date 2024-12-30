from . import *
import serial
import time

PORT = "/dev/ttyS0"
BAUD_RATE = 115200
TIME_OUT = 1
SERRIAL_OBJECT = None

# NOTE - If the user_comand itself is "", its better to restart the pi


def configure_serial():
    global SERRIAL_OBJECT
    SERRIAL_OBJECT = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)
    SERRIAL_OBJECT.write(b"AT+CMGF=1\r")
    user_command = SERRIAL_OBJECT.readline().decode().strip()  # Read the echoed command
    log_info(f"User Command : {user_command}")
    response = SERRIAL_OBJECT.readline().decode().strip()  # Read the actual response
    log_info(f"Response : {response}")
    time.sleep(2)


def send_sms_text(recipient_phone_number, sms_message) -> bool:
    if is_valid_phone_number(recipient_phone_number):
        configure_serial()
        SERRIAL_OBJECT.write(f'AT+CMGS="{recipient_phone_number}"\r'.encode())
        user_command = SERRIAL_OBJECT.readline().decode().strip()
        log_info(f"User Command : {user_command}")
        response = SERRIAL_OBJECT.readline().decode().strip()
        log_info(f"Response : {response}")

        time.sleep(2)

        SERRIAL_OBJECT.write(
            f"{sms_message}\x1A".encode()
        )  # \x1A is the ASCII code for Ctrl+Z
        user_command = SERRIAL_OBJECT.readline().decode().strip()
        log_info(f"User command : {user_command}")
        response = SERRIAL_OBJECT.readline().decode().strip()
        log_info(f"Response : {response}")

        time.sleep(2)
        SERRIAL_OBJECT.close()
        log_info(f"SMS to <{recipient_phone_number}> successful.")
        return True
    else:
        log_info(f"SMS to <{recipient_phone_number}> unsuccessful.")
        log_info(f"Phone number seems to be invalid.")
        return False
