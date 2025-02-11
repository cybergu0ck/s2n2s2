import serial
import time

PORT = "/dev/ttyS0"
BAUD_RATE = 115200
TIME_OUT = 3
LTE_MODULE = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)


def flush_input():
    LTE_MODULE.reset_input_buffer()


def flush_output():
    LTE_MODULE.reset_output_buffer()


def set_character_set(character_set: str) -> bool:
    res = False
    flush_output()
    if character_set == "UCS2":
        LTE_MODULE.write(b'AT+CSCS="UCS2"\r')
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        print(f"AT Command to set character set: {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            print(f"Response : {response}")
            res = True
        else:
            print("Character set not set.")
            print(f"Response : {response}")
            res = False
    elif character_set == "IRA":
        LTE_MODULE.write(b'AT+CSCS="IRA"\r')
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        print(f"AT Command to set character set: {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            print(f"Response : {response}")
            res = True
        else:
            print("Character set not set.")
            print(f"Response : {response}")
            res = False
    elif character_set == "GSM":
        LTE_MODULE.write(b'AT+CSCS="GSM"\r')
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        print(f"AT Command to set character set: {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            print(f"Response : {response}")
            res = True
        else:
            print("Character set not set.")
            print(f"Response : {response}")
            res = False
    else:
        print(
            "Unsupported character set. Supported character set are IRA, GSM and UCS2."
        )
        res = False
    flush_input()
    return res


def set_text_mode_parameters(is_non_english=False):
    """Set text mode parameters."""
    res = False
    flush_output()
    if is_non_english:
        LTE_MODULE.write(b"AT+CSMP=17,168,0,8\r")
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        print(f"AT Command to set text mode parameters: {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            print(f"Response : {response}")
            res = True
        else:
            print("Text mode parameters not set.")
            print(f"Response : {response}")
            res = False
    else:
        LTE_MODULE.write(b"AT+CSMP=17,168,0,0\r")
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        print(f"AT Command to set text mode parameters: {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            print(f"Response : {response}")
            res = True
        else:
            print("Text mode parameters not set.")
            print(f"Response : {response}")
            res = False
    flush_input()
    return res


def send_sms() -> bool:
    res = False
    phone_number = "+919632448895"
    sms_message = "Namaste, your Shashwatha Pooja Seva to Shri Shankara Narayana Swamy was performed today...Regards Temple Trustee, Naloor, Kadaba"
    flush_output()
    LTE_MODULE.write(f'AT+CMGS="{phone_number}"\r'.encode())
    time.sleep(2)
    at_command = LTE_MODULE.readline().decode().strip()
    print(f"AT Command to send message : {at_command}")
    response = LTE_MODULE.readline().decode().strip()
    if response == ">":
        LTE_MODULE.write(
            f"{sms_message}\x1A".encode()
        )  # \x1A is the ASCII code for Ctrl+Z
        time.sleep(2)
        print(LTE_MODULE.in_waiting)
        at_command = LTE_MODULE.readline().decode().strip()
        response_1 = LTE_MODULE.readline().decode().strip()
        response_2 = LTE_MODULE.readline().decode().strip()
        response_3 = LTE_MODULE.readline().decode().strip()
        print(f"AT Command with message : {at_command}")
        if response_1.startswith("+CMGS:") and response_3 == "OK":
            print(f"Response : {response_1}")
            print(f"Response : {response_2}")
            print(f"Response : {response_3}")
            res = True
        else:
            print(f"Message not sent.")
            print(f"Response : {response_1}")
            res = False
    else:
        print(f"Message not sent.")
        print(f"Response : {response}")
        res = False
    flush_input()
    return res


set_character_set("IRA")
set_text_mode_parameters(False)
send_sms()
