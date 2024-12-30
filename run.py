import serial
import time

PORT = "/dev/ttyS0"  # Adjust this as necessary for your system
BAUD_RATE = 115200
TIME_OUT = 3

# Initialize serial connection
SERRIAL_OBJECT = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)

# Set modem to Text Mode
SERRIAL_OBJECT.write(b"AT+CMGF=0\r")
response = SERRIAL_OBJECT.readline().decode().strip()
print(response)
time.sleep(2)

# Phone number and message
phone_num = "+919632448895"
msg = "ಅತ್ಮೀಯ ಶ್ರೀ ನಾಲೂರು ಶಂಕರ ನಾರಾಯಣ ಸ್ವಾಮಿಯ ಸೇವಾಕರ್ತರೆ"

# Sending Message
SERRIAL_OBJECT.write(f'AT+CMGS="{phone_num}"\r'.encode())
response = SERRIAL_OBJECT.readline().decode().strip()
print(response)
time.sleep(2)

# Encode the message in UCS2
msg_ucs2 = msg.encode("utf-16be")  # Encode as UCS2 (UTF-16BE)
msg_length = len(msg_ucs2) // 2  # Each character is 2 bytes

# Send the length of the message (in PDU mode) if needed; otherwise just send the message
SERRIAL_OBJECT.write(msg_ucs2 + b"\x1A")  # \x1A is the ASCII code for Ctrl+Z
time.sleep(2)

# Read response after sending the message
response = SERRIAL_OBJECT.readline().decode().strip()
print(response)

# Close the serial connection
SERRIAL_OBJECT.close()
