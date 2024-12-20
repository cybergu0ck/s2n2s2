#!/usr/bin/env python3
"""
  * This script access the google sheet, parses it and uses the relevant information to send messages via a client.
  * This script is supposed to be deployed on a raspberry pi where it will be executed on a schedule.
"""
"""
DEV NOTES:

NOTE - Keep the code simple and donot introduce unnecesary classes.
TODO - Add exception handling and in the case of exception send fail log to admin number
TODO - Add sim center number in the code
"""

import gspread
import os
import serial
import time
import logging
from datetime import datetime
from enum import Enum, auto


SHEETS_TITLE = "s2n2s2-db"
TODAY = datetime.today().strftime("%d/%m/%Y")
TODAY_FOR_LOG = datetime.today().strftime("%Y-%m-%d")
HEADER_ROW = 1

PORT = "/dev/ttyS0"
BAUD_RATE = 115200
TIME_OUT = 1
SERRIAL_OBJECT = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)

LOG_DIR_NAME = "logs"
LOG_FILE_EXTENSION = ".log"
PATH_TO_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_TO_LOG_DIR = os.path.join(PATH_TO_SCRIPT_DIR, LOG_DIR_NAME)

DEV_MODE = True


class SheetsHeader(Enum):
    RECEIPT_NUMBER = auto()
    RECEIPT_DATE = auto()
    REGISTERED_TITLE = auto()
    REGISTERED_NAME = auto()
    REGISTERED_DATE = auto()
    REGISTERED_GOTRA = auto()
    REGISTERED_NAKSHATRA = auto()
    REGISTERED_RASHI = auto()
    REGISTERED_PHONE_NUMBER = auto()
    REGISTERED_WHATSAPP_NUMBER = auto()


sheetsheader_to_internalreference = {
    "Receipt Number": SheetsHeader.RECEIPT_NUMBER,
    "Receipt Date": SheetsHeader.RECEIPT_DATE,
    "Title": SheetsHeader.REGISTERED_TITLE,
    "Name": SheetsHeader.REGISTERED_NAME,
    "Date": SheetsHeader.REGISTERED_DATE,
    "Gotra": SheetsHeader.REGISTERED_GOTRA,
    "Nakshatra": SheetsHeader.REGISTERED_NAKSHATRA,
    "Rashi": SheetsHeader.REGISTERED_RASHI,
    "Phone Number": SheetsHeader.REGISTERED_PHONE_NUMBER,
    "Whatsapp Number": SheetsHeader.REGISTERED_WHATSAPP_NUMBER,
}


def increment_filename(filename):
    res = ""
    seperator = "_"
    increment = 0
    filename_without_extension = filename.split(".")[0]
    if len(filename_without_extension.split(seperator)) == 1:
        increment += 1
    else:
        increment = int(filename_without_extension.split(seperator)[-1]) + 1

    res += filename_without_extension.split(seperator)[0] + seperator + str(increment)
    print(res)
    return res


def get_new_filename(filename):
    res = increment_filename(filename)
    path_to_new_filename = os.path.join(PATH_TO_LOG_DIR, res + LOG_FILE_EXTENSION)
    if os.path.exists(path_to_new_filename):
        return get_new_filename(res)
    return res


def get_logfile_path():
    path_to_log_file = os.path.join(
        PATH_TO_LOG_DIR, f"{TODAY_FOR_LOG}{LOG_FILE_EXTENSION}"
    )
    if os.path.exists(path_to_log_file):
        filename = str(os.path.basename(path_to_log_file))
        new_filename = get_new_filename(filename)
        path_to_log_file = os.path.join(
            PATH_TO_LOG_DIR, f"{new_filename}{LOG_FILE_EXTENSION}"
        )
    return path_to_log_file


def configure_logger():
    os.makedirs(PATH_TO_LOG_DIR, exist_ok=True)
    logging.basicConfig(
        filename=get_logfile_path(),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("logger configuration successful")


def is_valid_date(value):
    try:
        datetime.strptime(value, "%d/%m/%Y")
        return True
    except (ValueError, TypeError):
        return False


def get_internalheader_to_columnid(worksheet):
    """
    Returns a map with keys as internal header references (encoded column headings) and the values as columen id.
    - This ensures that script will not fail if columns are interchanged or modified.
    - The
    - Example: {nakshatra: 5, rashi : 6}
    """
    res = {}
    header_row_values = worksheet.row_values(HEADER_ROW)
    for id, header in enumerate(header_row_values):
        col_id = id + 1
        res[sheetsheader_to_internalreference[header]] = col_id
    return res


def get_todays_recepients(worksheet, internalheader_to_columnid):
    """
    Returns a list containing list of all the values of a row whose date corresponds to today's date.
    """
    res = []
    date_column_values = worksheet.col_values(
        internalheader_to_columnid[SheetsHeader.REGISTERED_DATE]
    )
    for row_id, cell_value in enumerate(date_column_values[1:], start=2):
        if is_valid_date(cell_value):
            if cell_value == TODAY:
                row_values = worksheet.row_values(row_id)
                res.append(row_values)
    return res


def get_custom_message(**kwargs):
    """
    Returns the custom text for the input parameters
    """

    res = f"Namasthe {kwargs.get('title')} {kwargs.get('name')}, Greetings from Naalur. As per Receipt Number {kwargs.get('receipt_num')}, dated {kwargs.get('receipt_date')}, Pooje has been done in the name of {kwargs.get('name')} of {kwargs.get('gotra')} Gotra, {kwargs.get('nakshatra')} Nakshtra, {kwargs.get('rashi')} Rashi. May the blessings of Naalur Devasthana always be with you."
    return res


def get_simple_message():
    return "Dear devotee of Lord Nalur Shankara Narayana Swamy, your Shashwatha Pooja Seva is performed today."


def configure_serial(SERRIAL_OBJECT):
    SERRIAL_OBJECT.write(b"AT+CMGF=1\r")  # Set the SMS message format to text mode
    user_command = SERRIAL_OBJECT.readline().decode().strip()  # Read the echoed command
    if DEV_MODE:
        print(f"\nuser command : {user_command}")

    response = SERRIAL_OBJECT.readline().decode().strip()  # Read the actual response
    if DEV_MODE:
        print(f"response : {response}\n")


def send_sms_text(recipient_phone_number, sms_message):
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


def send_whatsapp_text(number, text):
    """
    Sends the text over whatsapp to the provided number
    """
    # STUB - Work on this once the communication over sms is made stable


def main():
    configure_logger()
    logging.info("script execution started")
    gc = gspread.service_account()
    sheet = gc.open(SHEETS_TITLE)
    worksheet = sheet.sheet1

    internalheader_to_columnid = get_internalheader_to_columnid(worksheet)
    recipients = get_todays_recepients(worksheet, internalheader_to_columnid)

    for recipient in recipients:
        phone_num = (
            "+91"
            + recipient[
                internalheader_to_columnid[SheetsHeader.REGISTERED_PHONE_NUMBER]
            ]
        )
        simple_message = get_simple_message()
        send_sms_text(phone_num, simple_message)
    logging.info("script execution successful")


if __name__ == "__main__":
    main()
