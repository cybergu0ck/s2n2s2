#!/usr/bin/env python3
"""
  * This script access the google sheet, parses it and uses the relevant information to send messages via a client.
  * This script is supposed to be deployed on a raspberry pi where it will be executed on a schedule.
"""


import gspread
from libs.utilslib.utils import *
from libs.comslib.email import send_email
from libs.comslib.sms import send_sms_text
from libs.loggerlib.logger import LOGGER, configure_logging_system
from libs.corelib.core import (
    SHEETS_TITLE,
    INTERNALHEADER_TO_COLUMNID,
    SheetsHeader,
    get_todays_recepients,
    get_simple_message,
    save_devotee_data_image,
    log_todays_recipients,
    define_internalheader_to_columnid,
)


def main():
    configure_logging_system()
    LOGGER.debug("Script execution started")
    gc = gspread.service_account()
    sheet = gc.open(SHEETS_TITLE)
    worksheet = sheet.sheet1

    define_internalheader_to_columnid(
        worksheet
    )  # TODO - Think about this peice of code
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
