#!/usr/bin/env python3
"""
  * This script access the google sheet, parses it and uses the relevant information to send messages via a client.
  * This script is supposed to be deployed on a raspberry pi where it will be executed on a schedule.
"""


import gspread
from libs.utilslib.utils import *

from libs.loggerlib.logger import configure_logging_system, log_info
from libs.corelib.core import (
    SHEETS_TITLE,
    get_todays_recepients,
    save_devotee_data_image,
    log_todays_recipients,
    define_internalheader_to_columnid,
    preprocess_retrived_data,
    dispatch_messages_to_recipients,
)


def main():
    configure_logging_system()
    log_info("Script execution started")
    gc = gspread.service_account()
    sheet = gc.open(SHEETS_TITLE)
    worksheet = sheet.sheet1

    define_internalheader_to_columnid(
        worksheet
    )  # TODO - Think about this peice of code
    recipients = get_todays_recepients(worksheet)
    preprocess_retrived_data(recipients)
    log_todays_recipients(recipients)
    save_devotee_data_image(recipients)
    dispatch_messages_to_recipients(recipients)

    log_info("Script execution successful")


if __name__ == "__main__":
    main()
