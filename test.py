import serial
import time

PORT = "/dev/ttyS0"
BAUD_RATE = 115200
TIME_OUT = 3
LTE_MODULE = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)


def is_module_functioning() -> bool:
    """Returns True if the simcom lte module is functioning, else False."""
    time.sleep(2)
    LTE_MODULE.write(b"AT\r")
    at_command = LTE_MODULE.readline().decode().strip()
    print(f"AT Command to check if module is functioning : {at_command}")
    response = LTE_MODULE.readline().decode().strip()
    time.sleep(2)
    if response == "OK":
        print(f"Response : {response}")
        return True
    else:
        print(f"Module is not functioning correctly, restart is suggested.")
        print(f"Response : {response}")
        return False


def is_sim_inserted() -> bool:
    """Returns True if sim card is inserted in the simcom lte module, else False."""
    time.sleep(2)
    LTE_MODULE.write(b"AT+CIMI\r")
    at_command = LTE_MODULE.readline().decode().strip()
    print(f"AT Command to check if sim is inserted : {at_command}")
    response = LTE_MODULE.readline().decode().strip()
    time.sleep(2)
    if response == "+CME ERROR: SIM not inserted":
        print(f"Sim not inserted, ensure sim is properly inserted.")
        print(f"Response : {response}")
        return False
    else:
        print(f"Response : {response}")
        return True


def is_network_registered() -> bool:
    """Returns True if the simcom lte module is registred to a network, else False."""
    time.sleep(2)
    LTE_MODULE.write(b"AT+CREG?\r")
    at_command = LTE_MODULE.readline().decode().strip()
    print(f"AT Command to check network registration status: {at_command}")
    response = LTE_MODULE.readline().decode().strip()
    time.sleep(2)
    # Successful output will be like  "+CREG: 0,1"
    if response.startswith("+CREG:"):
        status = response.split(",")[1]
        if status == "0":
            print(
                f" Not registered,ME is not currently searching a new operator to register to."
            )
            print(f"Response : {response}")
            return False
        elif status == "1":
            print(f"Registered to home network.")
            print(f"Response : {response}")
            return True
        elif status == "2":
            print(f"Registered to home network.")
            print(f"Response : {response}")
            return False
        elif status == "3":
            print(f"Registration denied.")
            print(f"Response : {response}")
            return False
        elif status == "4":
            print(f"Unknown response while fetching network registration.")
            print(f"Response : {response}")
            return False
        elif status == "5":
            print(f"Registered, roaming.")
            print(f"Response : {response}")
            return True
        elif status == "6":
            print(f"Registered, sms only.")
            print(f"Response : {response}")
            return True
    else:
        print(f"Unable to fetch network registation detail.")
        print(f"Response : {response}")
        return False


if is_module_functioning():
    if is_sim_inserted():
        if is_network_registered():
            print("done")


# def unicode_to_hex(text):
#     return "".join(f"{ord(char):04x}" for char in text).upper()


# LTE_MODULE.write(b"ATZ\r")
# user_command = LTE_MODULE.readline().decode().strip()
# response = LTE_MODULE.readline().decode().strip()
# print(user_command)
# print(response)
# time.sleep(2)

# LTE_MODULE.write(b'AT+CSCS="UCS2"\r')
# user_command = LTE_MODULE.readline().decode().strip()
# response = LTE_MODULE.readline().decode().strip()
# print(user_command)
# print(response)
# time.sleep(2)

# LTE_MODULE.write(b"AT+CSMP=17,168,0,8\r")
# user_command = LTE_MODULE.readline().decode().strip()
# response = LTE_MODULE.readline().decode().strip()
# print(user_command)
# print(response)
# time.sleep(2)

# LTE_MODULE.write(b"AT+CMGF=1\r")
# user_command = LTE_MODULE.readline().decode().strip()
# response = LTE_MODULE.readline().decode().strip()
# print(user_command)
# print(response)
# time.sleep(2)


# phone_num = "+919632448895"
# # msg = "ತಮ್ಮ ಶಾಶ್ವತ ಸೇವಾ ಪೂಜೆಯನ್ನು ಇಂದು ನೆರವೇರಿಸಲಾಗಿದೆ."
# msg = "ನಿಮ್ಮ ನಾಲೂರು ಶಂಕರ ನಾರಾಯಣ ದೇವರ ಶಾಶ್ವತ ಪೂಜಾ ಸೇವೆ ಇಂದು ನಡೆಯಲಿದೆ"

# phone_num_hez = unicode_to_hex(phone_num)
# msg_hex = unicode_to_hex(msg)


# Sending Message
# print("Entering cmd to send message here")
# LTE_MODULE.write(f'AT+CMGS="{phone_num_hez}"\r'.encode())
# time.sleep(2)
# user_command = LTE_MODULE.readline().decode().strip()
# response = LTE_MODULE.readline().decode().strip()
# print(user_command)
# print(response)
# print("writing message here")
# LTE_MODULE.write(f"{msg_hex}\x1A".encode())  # \x1A is the ASCII code for Ctrl+Z
# user_command = LTE_MODULE.readline().decode().strip()
# response = LTE_MODULE.readline().decode().strip()
# print(user_command)
# print(response)
# print("1")
# response = LTE_MODULE.readline().decode().strip()
# print(response)
# print("2")
# response = LTE_MODULE.readline().decode().strip()
# print(response)
# time.sleep(2)
# LTE_MODULE.close()


# # Prepare the message in Kannada
# kannada_message = "ನಮಸ್ಕಾರ"  # This means "Hello"
# encoded_message = kannada_message.encode(
#     "utf-16-be"
# )  # Encode in UCS2 (UTF-16 Big Endian)

# LTE_MODULE.write(f"AT+CMGS={len(encoded_message)//2}".encode() + b"\r")
# time.sleep(1)  # Wait for response
# user_command = LTE_MODULE.readline().decode().strip()
# response = LTE_MODULE.readline().decode().strip()
# print(user_command)
# print(response)

# # Send the actual message
# LTE_MODULE.write(f"{encoded_message}\x1A".encode())
# time.sleep(3)
# user_command = LTE_MODULE.readline().decode().strip()
# response = LTE_MODULE.readline().decode("utf-8").strip()
# print("Final Response:", response)
# print(user_command)
# print(response)

# LTE_MODULE.close()


# # Sending Message
# LTE_MODULE.write(f'AT+CMGS="{phone_num}"\r'.encode())
# user_command = LTE_MODULE.readline().decode().strip()
# response = LTE_MODULE.readline().decode().strip()
# time.sleep(2)
# LTE_MODULE.write(f"{msg}\x1A".encode("utf-8"))  # \x1A is the ASCII code for Ctrl+Z
# user_command = LTE_MODULE.readline().decode().strip()
# response = LTE_MODULE.readline().decode().strip()
# print(user_command)
# print(response)
# response = LTE_MODULE.readline().decode().strip()
# print(response)
# response = LTE_MODULE.readline().decode().strip()
# print(response)
# time.sleep(2)
# LTE_MODULE.close()
