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
today_date = datetime.today().strftime("%d/%m/%Y")
# NOTE - The creds are stored as env variables
TWILIO_ACC_SSID = os.getenv("TWILIO_ACC_SSID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


# Global Functions
def is_date(value):
    try:
        datetime.strptime(value, "%m/%d/%Y")
        return True
    except (ValueError, TypeError):
        return False


def create_val_to_address_map(worksheet):
    headings = worksheet.row_values(1)  # TODO - This function can be written better
    row_map = {}
    for idx, value in enumerate(headings):
        # cell_address = f"{chr(65 + idx)}1"
        cell_address = idx + 1
        row_map[value] = cell_address
    return row_map


def get_rows_with_today_date(worksheet):
    matching_rows = []
    date_column_values = worksheet.col_values(heading_map["Date"])
    for row_idx, cell_value in enumerate(date_column_values[1:], start=2):
        if cell_value == today_date:
            row_values = worksheet.row_values(row_idx)
            matching_rows.append(row_values)
    return matching_rows


# Business Logic
def main():
    gc = gspread.service_account()
    sheet = gc.open("s2n2s2-db")
    worksheet = sheet.sheet1
    global heading_map
    heading_map = create_val_to_address_map(worksheet)
    todays_devotees = get_rows_with_today_date(worksheet)
    for devotee in todays_devotees:
        name = devotee[1]  # TODO - Work a way to get rid of the hardcoding
        receipt_date = devotee[2]
        receipt_num = devotee[3]
        gotra = devotee[5]
        nakshatra = devotee[6]
        rashi = devotee[7]
        phone_num = devotee[8]
        whatsapp_num = devotee[9]
        custom_message = f"Hello Mr.{name}, Greetings from Naalur. As per Receipt Number {receipt_num}, dated {receipt_date}, Pooje has been done in the name of {name} of {gotra} Gotra, {nakshatra} Nakshtra, {rashi} Rashi. May the blessings of Naalur Devasthana always be with you."
        account_sid = TWILIO_ACC_SSID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=custom_message,
            from_="whatsapp:+14155238886",
            to="whatsapp:+" + whatsapp_num,
        )


if __name__ == "__main__":
    main()
