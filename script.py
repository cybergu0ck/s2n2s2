#!/usr/bin/env python3
"""
  * This script access the google sheet, parses it and uses the relevant information to send messages via a client.
  * This script is supposed to be deployed in a server where it will be executed once, everyday.
"""

import gspread
from datetime import datetime
import os
from twilio.rest import Client


# DEVNOTE - Choosing not to create a class (atleast in this stage) and proceeding with global variables and global utility functions to keep it simple and functional.


# Global Variables
GOOGLE_SHEETS_TITLE = "s2n2s2-db"

TODAY = datetime.today().strftime("%d/%m/%Y")
HEADER_ROW = 1

RECEIPT_NUMBER = 1
RECEIPT_DATE = 2
REGISTERED_TITLE = 3
REGISTERED_NAME = 4
REGISTERED_DATE = 5
REGISTERED_GOTRA = 6
REGISTERED_NAKSHATRA = 7
REGISTERED_RASHI = 8
REGISTERED_PHONE_NUMBER = 9
REGISTERED_WHATSAPP_NUMBER = 10

HEADER_ENCODING = {
    "Receipt Number": RECEIPT_NUMBER,
    "Receipt Date": RECEIPT_DATE,
    "Title": REGISTERED_TITLE,
    "Name": REGISTERED_NAME,
    "Date": REGISTERED_DATE,
    "Gotra": REGISTERED_GOTRA,
    "Nakshatra": REGISTERED_NAKSHATRA,
    "Rashi": REGISTERED_RASHI,
    "Phone Number": REGISTERED_PHONE_NUMBER,
    "Whatsapp Number": REGISTERED_WHATSAPP_NUMBER,
}

# NOTE - The creds are stored as env variables
TWILIO_ACC_SSID = os.getenv("TWILIO_ACC_SSID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


# Global Functions
def is_valid_date(value):
    try:
        datetime.strptime(value, "%d/%m/%Y")
        return True
    except (ValueError, TypeError):
        return False


def get_encoded_header_id_map(worksheet):
    """
    Returns a map with keys as encoded headers (encoded column headings) and the values as columen id.
    - This ensures that script will not fail if columns are interchanged or modified.
    - The
    - Example: {nakshatra: 5, rashi : 6}
    """
    res = {}
    header_row_values = worksheet.row_values(HEADER_ROW)
    for id, header in enumerate(header_row_values):
        col_id = id + 1
        res[HEADER_ENCODING[header]] = col_id
    return res


def get_todays_recepients(worksheet, encoded_header_to_id):
    """
    Returns a list containing list of all the values of a row whose date corresponds to today's date.
    """
    res = []
    date_column_values = worksheet.col_values(encoded_header_to_id["date"])
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


def send_whatsapp_text(text, number):
    """
    Sends the text over whatsapp to the provided number
    """
    account_sid = TWILIO_ACC_SSID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=text,
        from_="whatsapp:+14155238886",
        to="whatsapp:+" + number,
    )


# Business Logic
def main():
    # TODO - Add exception handling and in the case of exception send fail log to admin number
    gc = gspread.service_account()
    sheet = gc.open(GOOGLE_SHEETS_TITLE)
    worksheet = sheet.sheet1
    encoded_header_to_id = get_encoded_header_id_map(worksheet)
    recipients = get_todays_recepients(worksheet, encoded_header_to_id)
    for recipient in recipients:
        phone_num = recipient[encoded_header_to_id[REGISTERED_PHONE_NUMBER]]
        whatsapp_num = recipient[encoded_header_to_id[REGISTERED_WHATSAPP_NUMBER]]
        custom_message = get_custom_message(
            title=recipient[encoded_header_to_id[REGISTERED_TITLE]],
            name=recipient[encoded_header_to_id[REGISTERED_NAME]],
            receipt_num=recipient[encoded_header_to_id[RECEIPT_NUMBER]],
            receipt_date=recipient[encoded_header_to_id[REGISTERED_DATE]],
            gotra=recipient[encoded_header_to_id[REGISTERED_GOTRA]],
            nakshatra=recipient[encoded_header_to_id[REGISTERED_NAKSHATRA]],
            rashi=recipient[encoded_header_to_id[REGISTERED_RASHI]],
        )
        send_whatsapp_text(custom_message, whatsapp_num)
        # TODO - Similarly send sms text


if __name__ == "__main__":
    main()
