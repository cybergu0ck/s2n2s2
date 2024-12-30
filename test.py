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
SERRIAL_OBJECT.write(b"AT+CMGF=1\r")
user_command = SERRIAL_OBJECT.readline().decode().strip()
response = SERRIAL_OBJECT.readline().decode().strip()
print(user_command)
print(response)
time.sleep(2)

phone_num = "9632448895"
msg = "ಅತ್ಮೀಯ ಶ್ರೀ ನಾಲೂರು ಶಂಕರ ನಾರಾಯಣ ಸ್ವಾಮಿಯ ಸೇವಾಕರ್ತರೆ"
msg = "hi"
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
