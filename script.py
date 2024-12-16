#!/usr/bin/env python3
"""
  * This script access the google sheet, parses it and uses the relevant information to send messages via a client.
  * This script is supposed to be deployed in a server where it will be executed once, everyday.
"""
"""
DEV NOTES:

Keep the code simple and donot introduce unnecesary classes.
Add exception handling and in the case of exception send fail log to admin number
"""


import gspread
import os
from datetime import datetime
from enum import Enum, auto

SHEETS_TITLE = "s2n2s2-db"
TODAY = datetime.today().strftime("%d/%m/%Y")
HEADER_ROW = 1


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


def send_whatsapp_text(number, text):
    """
    Sends the text over whatsapp to the provided number
    """
    # STUB - Work on this once the communication over sms is made stable


def main():
    gc = gspread.service_account()
    sheet = gc.open(SHEETS_TITLE)
    worksheet = sheet.sheet1

    internalheader_to_columnid = get_internalheader_to_columnid(worksheet)
    recipients = get_todays_recepients(worksheet, internalheader_to_columnid)
    for recipient in recipients:
        phone_num = recipient[
            internalheader_to_columnid[SheetsHeader.REGISTERED_PHONE_NUMBER]
        ]
        whatsapp_num = recipient[
            internalheader_to_columnid[SheetsHeader.REGISTERED_WHATSAPP_NUMBER]
        ]
        custom_message = get_custom_message(
            title=recipient[internalheader_to_columnid[SheetsHeader.REGISTERED_TITLE]],
            name=recipient[internalheader_to_columnid[SheetsHeader.REGISTERED_NAME]],
            receipt_num=recipient[
                internalheader_to_columnid[SheetsHeader.RECEIPT_NUMBER]
            ],
            receipt_date=recipient[
                internalheader_to_columnid[SheetsHeader.REGISTERED_DATE]
            ],
            gotra=recipient[internalheader_to_columnid[SheetsHeader.REGISTERED_GOTRA]],
            nakshatra=recipient[
                internalheader_to_columnid[SheetsHeader.REGISTERED_NAKSHATRA]
            ],
            rashi=recipient[internalheader_to_columnid[SheetsHeader.REGISTERED_RASHI]],
        )

        # TODO - Similarly send sms text


if __name__ == "__main__":
    main()
