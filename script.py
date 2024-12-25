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
TODO - Add whatsapp support
TODO - figure out the mechanism for sending coms
TODO - Calculate the size of sd card needed based on log files generated or figure out a way to clean the log files
"""

import gspread
import os
import serial
import time
import logging
import matplotlib.pyplot as plt
import numpy as np
import shutil
from datetime import datetime
from enum import Enum, auto
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

DEV_MODE = True
PI_MODE = False

SHEETS_TITLE = "s2n2s2-db"
TODAY = datetime.today().strftime("%d/%m/%Y")
TODAY_FOR_LOG = datetime.today().strftime("%Y-%m-%d")
HEADER_ROW = 1

PORT = "/dev/ttyS0"
BAUD_RATE = 115200
TIME_OUT = 1
if PI_MODE:
    global SERRIAL_OBJECT
    SERRIAL_OBJECT = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)

LOG_DIR_NAME = "logs"
DEV_LOG_DIR_NAME = "dev-logs"
ADMIN_LOG_DIR_NAME = "admin-logs"
DEV_LOG_FILE_EXTENSION = ".txt"
ADMIN_LOG_FILE_EXTENSION = ".doc"
PATH_TO_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGGER = logging.getLogger()

TEMP_DIR_NAME = "temp"
IMAGE_NAME = "devotee-data.png"

SENDER_EMAIL_ADDRESS = os.environ.get("S2N2S2-EMAIL")
SENDER_EMAIL_KEY = os.environ.get("S2N2S2-EMAIL-KEY")


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
    return res


def get_new_filename(filename, is_dev):
    res = increment_filename(filename)
    path = PATH_TO_DEV_LOG_DIR if is_dev else PATH_TO_ADMIN_LOG_DIR
    file_extension = DEV_LOG_FILE_EXTENSION if is_dev else ADMIN_LOG_FILE_EXTENSION
    path_to_new_filename = os.path.join(path, res + file_extension)
    if os.path.exists(path_to_new_filename):
        return get_new_filename(res, is_dev)
    return res


def get_logfile_path(is_dev):
    path = PATH_TO_DEV_LOG_DIR if is_dev else PATH_TO_ADMIN_LOG_DIR
    file_extension = DEV_LOG_FILE_EXTENSION if is_dev else ADMIN_LOG_FILE_EXTENSION
    path_to_log_file = os.path.join(path, f"{TODAY_FOR_LOG}{file_extension}")
    if os.path.exists(path_to_log_file):
        filename = str(os.path.basename(path_to_log_file))
        new_filename = get_new_filename(filename, is_dev)
        path_to_log_file = os.path.join(path, f"{new_filename}{file_extension}")
    return path_to_log_file


def create_log_directories():
    if not os.path.exists(LOG_DIR_NAME):
        os.makedirs(LOG_DIR_NAME)

    global PATH_TO_LOG_DIR
    PATH_TO_LOG_DIR = os.path.join(PATH_TO_SCRIPT_DIR, LOG_DIR_NAME)

    dev_log_dir = os.path.join(PATH_TO_LOG_DIR, DEV_LOG_DIR_NAME)
    if not os.path.exists(dev_log_dir):
        os.makedirs(f"{LOG_DIR_NAME}/{DEV_LOG_DIR_NAME}")

    global PATH_TO_DEV_LOG_DIR
    PATH_TO_DEV_LOG_DIR = os.path.join(PATH_TO_LOG_DIR, DEV_LOG_DIR_NAME)

    admin_log_dir = os.path.join(PATH_TO_LOG_DIR, ADMIN_LOG_DIR_NAME)
    if not os.path.exists(admin_log_dir):
        os.makedirs(f"{LOG_DIR_NAME}/{ADMIN_LOG_DIR_NAME}")

    global PATH_TO_ADMIN_LOG_DIR
    PATH_TO_ADMIN_LOG_DIR = os.path.join(PATH_TO_LOG_DIR, ADMIN_LOG_DIR_NAME)


def configure_logging_system():
    create_log_directories()

    LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug("Logger configuration successful")

    debug_handler = logging.FileHandler(get_logfile_path(True))
    debug_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    debug_handler.setFormatter(debug_formatter)
    debug_handler.setLevel(logging.DEBUG)
    LOGGER.addHandler(debug_handler)

    info_handler = logging.FileHandler(get_logfile_path(False))
    info_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    info_handler.setFormatter(info_formatter)
    info_handler.setLevel(logging.INFO)
    LOGGER.addHandler(info_handler)
    LOGGER.debug("Logger system configured successfully")


def is_valid_date(value):
    try:
        datetime.strptime(value, "%d/%m/%Y")
        return True
    except (ValueError, TypeError):
        return False


def define_internalheader_to_columnid(worksheet):
    """
    Defines a map with keys as internal header references (encoded column headings) and the values as columen id.
    Defines a map with keys as internal header references (encoded column headings) and the values as columen id.
    - This ensures that script will not fail if columns are interchanged or modified.
    - The
    - Example: {nakshatra: 5, rashi : 6}
    """
    global INTERNALHEADER_TO_COLUMNID
    INTERNALHEADER_TO_COLUMNID = {}
    header_row_values = worksheet.row_values(HEADER_ROW)
    for id, header in enumerate(header_row_values):
        col_id = id + 1
        INTERNALHEADER_TO_COLUMNID[sheetsheader_to_internalreference[header]] = col_id


def get_todays_recepients(worksheet):
    """
    Returns a list containing list of all the values of a row whose date corresponds to today's date.
    """
    res = []
    date_column_values = worksheet.col_values(
        INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_DATE]
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


def send_email(email_address, subject, body, attachements):
    """
    Sends an email.
    Args:
        email_address: Receiver's email address
        subject: Subject of the email
        body: Body of the email
        attachements : array of dict's containing path of the file to be attached and name to be given of the attached file.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    context = ssl.create_default_context()

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL_ADDRESS
    message["To"] = email_address
    body_part = MIMEText(body)
    message.attach(body_part)

    for attachement in attachements:
        with open(attachement["path"], "rb") as file:
            message.attach(MIMEApplication(file.read(), Name=attachement["name"]))

    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(SENDER_EMAIL_ADDRESS, SENDER_EMAIL_KEY)
        server.send_message(message)


def send_whatsapp_text(number, text):
    """
    Sends the text over whatsapp to the provided number
    """
    # STUB - Work on this once the communication over sms is made stable


def log_todays_recipients(recipients):
    list_of_names = f"""List of recipients:"""

    for recipient in recipients:
        title = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_TITLE] - 1]
        name = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_NAME] - 1]
        list_of_names += f"\n\t\t\t\t\t\t\t\t- {title} {name}"

    LOGGER.info(list_of_names)


def save_devotee_data_image(recipients):
    header_row = []
    for i in range(1, len(recipients[0]) + 1):
        key = next((k for k, v in INTERNALHEADER_TO_COLUMNID.items() if v == i), None)
        original_name = next(
            (k for k, v in sheetsheader_to_internalreference.items() if v == key), None
        )
        header_row.append(original_name)
    recipients.insert(0, header_row)
    data = np.array(recipients)

    fig, ax = plt.subplots(figsize=(12, 8))
    table = ax.table(cellText=data, cellLoc="center", loc="top")
    table.auto_set_font_size(True)
    table.auto_set_column_width(col=list(range(len(recipients[0]))))
    # custom dimensioning
    # table.set_fontsize(8)
    # table.scale(2, 1.3)
    ax.set_axis_off()

    global PATH_TO_TEMP_DIR
    PATH_TO_TEMP_DIR = os.path.join(PATH_TO_SCRIPT_DIR, TEMP_DIR_NAME)
    if os.path.exists(PATH_TO_TEMP_DIR):
        shutil.rmtree(PATH_TO_TEMP_DIR)
    os.makedirs(TEMP_DIR_NAME)
    path_to_image = os.path.join(PATH_TO_TEMP_DIR, IMAGE_NAME)
    plt.savefig(path_to_image, dpi=300)


def main():
    configure_logging_system()
    LOGGER.debug("Script execution started")
    gc = gspread.service_account()
    sheet = gc.open(SHEETS_TITLE)
    worksheet = sheet.sheet1

    define_internalheader_to_columnid(worksheet)
    recipients = get_todays_recepients(worksheet)
    log_todays_recipients(recipients)
    save_devotee_data_image(recipients)

    for recipient in recipients:
        title = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_TITLE] - 1]
        name = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_NAME] - 1]
        phone_num = (
            "+91"
            + recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_PHONE_NUMBER] - 1
            ]
        )
        gotra = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_GOTRA] - 1]
        rashi = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_RASHI] - 1]
        nakshatra = recipient[
            INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_NAKSHATRA] - 1
        ]

        recipient_info = f"""Following data is processed for {title} {name} :\n\t\t\t\t\t\t\t\t- Name : {name}\n\t\t\t\t\t\t\t\t- Phone Number : {phone_num}\n\t\t\t\t\t\t\t\t- Astrological Info : {gotra}/{rashi}/{nakshatra}"""
        LOGGER.info(recipient_info)

        simple_message = get_simple_message()
        LOGGER.info(f"Sending SMS to {title} {name}")
        if PI_MODE:
            send_sms_text(phone_num, simple_message)
            LOGGER.info(f"SMS sent successfully to {title} {name}")
    LOGGER.debug("Script execution successful")


if __name__ == "__main__":
    main()
