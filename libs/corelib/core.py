from . import *
from libs.comslib.email import send_email
from libs.comslib.sms import send_sms_text
import time
import shutil
from enum import Enum, auto
import matplotlib.pyplot as plt
import numpy as np
import json

SHEETS_TITLE = "s2n2s2-db"
HEADER_ROW = 1

TEMP_DIR_NAME = "temp"
IMAGE_NAME = "devotees-list.png"


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
    REGISTERED_EMAIL = auto()


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
    "Email Address": SheetsHeader.REGISTERED_EMAIL,
}

INTERNALHEADER_TO_COLUMNID = {}


def define_internalheader_to_columnid(worksheet):
    """
    Defines a map with keys as internal header references (encoded column headings) and the values as columen id.
    Defines a map with keys as internal header references (encoded column headings) and the values as columen id.
    - This ensures that script will not fail if columns are interchanged or modified.
    - The
    - Example: {nakshatra: 5, rashi : 6}
    """
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


def log_todays_recipients(recipients):
    list_of_names = f"""List of recipients:"""

    for recipient in recipients:
        title = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_TITLE] - 1]
        name = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_NAME] - 1]
        list_of_names += f"\n\t\t\t\t\t\t\t\t- {title} {name}"
    log_info(list_of_names)


def save_devotee_data_image(recipients):
    recipients_copy = recipients.copy()
    header_row = []
    for i in range(1, get_num_cols() + 1):
        key = next((k for k, v in INTERNALHEADER_TO_COLUMNID.items() if v == i), None)
        original_name = next(
            (k for k, v in sheetsheader_to_internalreference.items() if v == key), None
        )
        header_row.append(original_name)

    recipients_copy.insert(0, header_row)
    data = np.array(recipients_copy)

    fig, ax = plt.subplots(figsize=(12, 8))
    table = ax.table(cellText=data, cellLoc="center", loc="top")
    table.auto_set_font_size(True)
    table.auto_set_column_width(col=list(range(len(recipients_copy[0]))))
    # custom dimensioning
    # table.set_fontsize(8)
    # table.scale(2, 1.3)
    ax.set_axis_off()

    global PATH_TO_TEMP_DIR
    PATH_TO_TEMP_DIR = os.path.join(PATH_TO_ROOT_DIR, TEMP_DIR_NAME)
    if os.path.exists(PATH_TO_TEMP_DIR):
        shutil.rmtree(PATH_TO_TEMP_DIR)
    os.makedirs(TEMP_DIR_NAME)
    path_to_image = os.path.join(PATH_TO_TEMP_DIR, IMAGE_NAME)
    plt.savefig(path_to_image, dpi=300)


def get_recipient_email_body(title, name):
    return f"""Namasthe dear devotee, {title} {name}. Greetings of the day from Nalur Shankara Narayana Devasthana. Your Shashwatha Pooja Seva is performed today. May the lord Shankara Narayana bless you and your family members. We look forward for your continuous support. \n\n - Temple Committee"""


def get_recipient_email_attachement():
    res = []
    standard_image = {}
    standard_image["path"] = PATH_TO_ROOT_DIR + "\\assets\\images\\standard.jpeg"
    standard_image["name"] = "NalurShankaraNarayana.jpeg"
    res.append(standard_image)
    return res


def get_admin_email_body(name, no_mail):
    if no_mail:
        return f"""Namasthe dear admin, {name}. Greetings of the day from Nalur Shankara Narayana Devasthana. There is NO Shashwatha Pooja Seva today, {TODAY}.\n\n\n-Admin Team"""
    else:
        return f"""Namasthe dear admin, {name}. Greetings of the day from Nalur Shankara Narayana Devasthana. Please find attached the log files along with an image that contains the list of recipients for whom the pooja is scheduled to be performed today, {TODAY}. Additionally, the confirmation messages that need to be sent for the same.\n\n\n-Admin Team"""


def get_admin_email_attachment():
    res = []
    devotee_image = {}
    devotee_image["path"] = PATH_TO_TEMP_DIR + "\\" + IMAGE_NAME
    devotee_image["name"] = IMAGE_NAME
    res.append(devotee_image)
    log_file = {}
    log_file["path"] = get_path_to_current_session_log(False)
    log_file["name"] = get_path_to_current_session_log(False).split("\\")[-1]
    res.append(log_file)
    return res


def get_num_cols():
    return len(sheetsheader_to_internalreference)


def append_empty_values(recipient, diff):
    for i in range(diff):
        recipient.append("")


def preprocess_retrived_data(recipients):
    """
    It is observed that if the last cells in a row are empty then these cells are complemetly ommitted by gspread api while retrieving the values. This function is to handle this.
    """
    num_cols = get_num_cols()
    for recipient in recipients:
        if len(recipient) != num_cols:
            diff = num_cols - len(recipient)
            append_empty_values(recipient, diff)


def dispatch_message_to_admins(recipients):
    path = PATH_TO_ROOT_DIR + "\\users\\users.json"
    with open(path, "r") as file:
        data = json.load(file)
        users = data["users"]
        for user in users:
            if user["admin_privilege"]:
                for email in user["email"]:
                    subject = "Daily Notification"
                    attachments = get_admin_email_attachment()
                    body = ""
                    if len(recipients):
                        body = get_admin_email_body(user["name"], False)
                    else:
                        body = get_admin_email_body(user["name"], True)
                    send_email(email, subject, body, attachments)
    log_info(f"Email sent successfully to admins")


def dispatch_messages_to_recipients(recipients):
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
            body = get_recipient_email_body(title, name)
            attachments = get_recipient_email_attachement()
            send_email(email_address, subject, body, attachments)
            log_info(f"Email sent successfully to {title} {name}")
        else:
            log_info(f"Email not sent to {title} {name}")

        time.sleep(4)
