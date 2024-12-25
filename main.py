#!/usr/bin/env python3
"""
  * This script access the google sheet, parses it and uses the relevant information to send messages via a client.
  * This script is supposed to be deployed on a raspberry pi where it will be executed on a schedule.
"""


import gspread
import time
from libs.utilslib.utils import *
from libs.comslib.email import send_email
from libs.comslib.sms import send_sms_text
from libs.loggerlib.logger import configure_logging_system, log_info
from libs.corelib.core import (
    SHEETS_TITLE,
    INTERNALHEADER_TO_COLUMNID,
    SheetsHeader,
    get_todays_recepients,
    get_simple_message,
    save_devotee_data_image,
    log_todays_recipients,
    define_internalheader_to_columnid,
    get_standard_email_body,
    get_standard_email_attachement,
    process_data,
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
    process_data(recipients)
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
        email_address = recipient[
            INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_EMAIL] - 1
        ]
        gotra = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_GOTRA] - 1]
        rashi = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_RASHI] - 1]
        nakshatra = recipient[
            INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_NAKSHATRA] - 1
        ]

        recipient_info = f"""Following data is processed for {title} {name} :\n\t\t\t\t\t\t\t\t- Name : {name}\n\t\t\t\t\t\t\t\t- Phone Number : {phone_num}\n\t\t\t\t\t\t\t\t- Astrological Info : {gotra}/{rashi}/{nakshatra}"""
        log_info(recipient_info)

        simple_message = get_simple_message()
        log_info(f"Sending SMS to {title} {name}")
        if PI_MODE:
            # STUB - phone number validation goes here
            send_sms_text(phone_num, simple_message)
            log_info(f"SMS sent successfully to {title} {name}")

        log_info(f"Sending email to {title} {name}")
        if (
            email_address != ""
        ):  # STUB - proper email validation here instead of this check
            subject = "Confirmation : Shashwatha Pooja Seva"
            body = get_standard_email_body(title, name)
            attachments = get_standard_email_attachement()
            send_email(email_address, subject, body, attachments)
            log_info(f"Email sent successfully to {title} {name}")
        else:
            log_info(f"Email not sent to {title} {name}")

        time.sleep(4)

    log_info("Script execution successful")


if __name__ == "__main__":
    main()
