import serial
import time

PORT = "/dev/ttyS0"
BAUD_RATE = 115200
TIME_OUT = 3
LTE_MODULE = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)


def send_sms():
    phone_num = "+919632448895"
    sms_message = "Namaste, your Shashwatha Pooja Seva to Shri Shankara Narayana Swamy was performed today...Regards Temple Trustee, Naloor, Kadaba"
    LTE_MODULE.write(f'AT+CMGS="{phone_num}"\r'.encode())
    at_command = LTE_MODULE.readline().decode().strip()
    print(f"AT Command to send message : {at_command}")
    response = LTE_MODULE.readline().decode().strip()
    if response == ">":
        LTE_MODULE.write(
            f"{sms_message}\x1A".encode()
        )  # \x1A is the ASCII code for Ctrl+Z
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        print(f"AT Command with message : {at_command}")
        response_1 = LTE_MODULE.readline().decode().strip()
        response_2 = LTE_MODULE.readline().decode().strip()
        response_3 = LTE_MODULE.readline().decode().strip()
        if response_1.startswith("+CMGS:") and response_3 == "OK":
            print(f"Response : {response_1}")
            print(f"Response : {response_2}")
            print(f"Response : {response_3}")
        else:
            print(f"Message not sent.")
            print(f"Response : {response_1}")
    else:
        print(f"Message not sent.")
        print(f"Response : {response}")


send_sms()
