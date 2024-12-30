import serial
import time

PORT = "/dev/ttyS0"
BAUD_RATE = 115200
TIME_OUT = 3
SERRIAL_OBJECT = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)

# Send basic AT command, expect the response to be OK
SERRIAL_OBJECT.write(b"AT\r")
user_command = SERRIAL_OBJECT.readline().decode().strip()
response = SERRIAL_OBJECT.readline().decode().strip()
print(user_command)
print(response)
time.sleep(2)

# Setting the mode or something
SERRIAL_OBJECT.write(b"AT+CMGF=0\r")
user_command = SERRIAL_OBJECT.readline().decode().strip()
response = SERRIAL_OBJECT.readline().decode().strip()
print(user_command)
print(response)
time.sleep(2)

SERRIAL_OBJECT.write(b'AT+CSCS="UCS2"\r')
user_command = SERRIAL_OBJECT.readline().decode().strip()
response = SERRIAL_OBJECT.readline().decode().strip()
print(user_command)
print(response)
time.sleep(2)

phone_num = "+919632448895"
msg = "0x59 0x6f"

# Sending Message
SERRIAL_OBJECT.write(f'AT+CMGS="{phone_num}"\r'.encode())
user_command = SERRIAL_OBJECT.readline().decode().strip()
response = SERRIAL_OBJECT.readline().decode().strip()
time.sleep(2)
SERRIAL_OBJECT.write(f"{msg}\x1A".encode())  # \x1A is the ASCII code for Ctrl+Z
user_command = SERRIAL_OBJECT.readline().decode().strip()
response = SERRIAL_OBJECT.readline().decode().strip()
print(user_command)
print(response)
response = SERRIAL_OBJECT.readline().decode().strip()
print(response)
response = SERRIAL_OBJECT.readline().decode().strip()
print(response)
time.sleep(2)
SERRIAL_OBJECT.close()


# # Prepare the message in Kannada
# kannada_message = "ನಮಸ್ಕಾರ"  # This means "Hello"
# encoded_message = kannada_message.encode(
#     "utf-16-be"
# )  # Encode in UCS2 (UTF-16 Big Endian)

# SERRIAL_OBJECT.write(f"AT+CMGS={len(encoded_message)//2}".encode() + b"\r")
# time.sleep(1)  # Wait for response
# user_command = SERRIAL_OBJECT.readline().decode().strip()
# response = SERRIAL_OBJECT.readline().decode().strip()
# print(user_command)
# print(response)

# # Send the actual message
# SERRIAL_OBJECT.write(f"{encoded_message}\x1A".encode())
# time.sleep(3)
# user_command = SERRIAL_OBJECT.readline().decode().strip()
# response = SERRIAL_OBJECT.readline().decode("utf-8").strip()
# print("Final Response:", response)
# print(user_command)
# print(response)

# SERRIAL_OBJECT.close()


# # Sending Message
# SERRIAL_OBJECT.write(f'AT+CMGS="{phone_num}"\r'.encode())
# user_command = SERRIAL_OBJECT.readline().decode().strip()
# response = SERRIAL_OBJECT.readline().decode().strip()
# time.sleep(2)
# SERRIAL_OBJECT.write(f"{msg}\x1A".encode("utf-8"))  # \x1A is the ASCII code for Ctrl+Z
# user_command = SERRIAL_OBJECT.readline().decode().strip()
# response = SERRIAL_OBJECT.readline().decode().strip()
# print(user_command)
# print(response)
# response = SERRIAL_OBJECT.readline().decode().strip()
# print(response)
# response = SERRIAL_OBJECT.readline().decode().strip()
# print(response)
# time.sleep(2)
# SERRIAL_OBJECT.close()
