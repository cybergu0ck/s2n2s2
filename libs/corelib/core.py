from . import *
from libs.comslib.email import send_email
from libs.comslib.sms import dispatch_sms, close_serial
import gspread
import time
import inspect
from enum import Enum, auto
import matplotlib.pyplot as plt
import numpy as np

SHEETS_TITLE = "shashwatha-seva-db"
WORKSHEET_PROD_NAME = "prod"
WORKSHEET_DEV_NAME = "dev"
WORKSHEET_ADMIN_NAME = "admins"
WORKSHEET_PUROHIT_NAME = "purohits"
WORKSHEET = None
ADMIN_WORKSHEET = None
PUROHIT_WORKSHEET = None
HEADER_ROW = 1
INTERNALHEADER_TO_COLUMNID = {}

IMAGE_NAME = "recipients-list.png"


class Member:
    def __init__(self, name, email, phone_number):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.whatsapp_number = None


ADMIN_WORKHEET_HEADER_INTEGRITY = [
    "Name",
    "Email Address",
    "Phone Number",
    "Whatsapp Number",
]

ADMINS = []
PUROHITS = []


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
    REGISTERED_LANGUAGE = auto()
    REGISTERED_BOOK_NUMBER = auto()


# ANCHOR - Here
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
    "Language": SheetsHeader.REGISTERED_LANGUAGE,
    "Book Number": SheetsHeader.REGISTERED_BOOK_NUMBER,
}


def get_num_cols():
    return len(sheetsheader_to_internalreference)


def load_google_sheet() -> bool:
    frame = inspect.currentframe()

    try:
        gc = gspread.service_account()
        sheet = gc.open(SHEETS_TITLE)
        global WORKSHEET
        if DEV_MODE:
            WORKSHEET = sheet.worksheet(WORKSHEET_DEV_NAME)
        else:
            WORKSHEET = sheet.worksheet(WORKSHEET_PROD_NAME)
        global ADMIN_WORKSHEET
        ADMIN_WORKSHEET = sheet.worksheet(WORKSHEET_ADMIN_NAME)
        global PUROHIT_WORKSHEET
        PUROHIT_WORKSHEET = sheet.worksheet(WORKSHEET_PUROHIT_NAME)
        log_debug(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        log_error(f"{get_function_name(frame)} unsuccessful.")
        log_error(f"Exception : {e}")
        return False


def populate_header_to_column_mapping() -> bool:
    """
    Populates a map with keys as internal header references (encoded column headings) and the values as columen id.
    Populates a map with keys as internal header references (encoded column headings) and the values as columen id.
    - This ensures that script will not fail if columns are interchanged or modified.
    - The
    - Example: {nakshatra: 5, rashi : 6}
    """
    frame = inspect.currentframe()

    try:
        global INTERNALHEADER_TO_COLUMNID
        header_row_values = WORKSHEET.row_values(HEADER_ROW)
        for id, header in enumerate(header_row_values):
            col_id = id + 1
            INTERNALHEADER_TO_COLUMNID[sheetsheader_to_internalreference[header]] = (
                col_id
            )
        log_debug(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        log_error(f"{get_function_name(frame)} unsuccessful.")
        log_error(f"Error found in internal header mapping code.")
        log_error(
            f"Check if the header names in the worksheet and in sheetsheader_to_internalreference consistant."
        )
        log_error(f"Exception : {e}")
        return False


def validate_admin_worksheet_header_integrity() -> bool:
    frame = inspect.currentframe()

    header_row = ADMIN_WORKSHEET.row_values(1)
    if header_row == ADMIN_WORKHEET_HEADER_INTEGRITY:
        log_debug(f"{get_function_name(frame)} successful.")
        return True
    else:
        log_error(f"{get_function_name(frame)} unsuccessful. ")
        log_error(f"The admin workheet header seems to be modified.")
        return False


def populate_admin_list() -> bool:
    frame = inspect.currentframe()

    admin_name_col = ADMIN_WORKSHEET.col_values(1)
    for row_id, cell_value in enumerate(admin_name_col[1:], start=2):
        row_values = ADMIN_WORKSHEET.row_values(row_id)
        if row_values == []:
            continue
        admin_obj = Member(
            row_values[0],
            row_values[1],
            row_values[2],
        )  # REVIEW - Hardcoded, infact the code related to admin is not written according to clean code practices, revist some time later
        ADMINS.append(admin_obj)

    if len(ADMINS) == 0:
        log_warning(f"{get_function_name(frame)} unsuccessful.")
        log_warning(f"Fetched zero admin from the admin worksheet.")
        log_warning(f"Early termination as atleast one admin is needed to proceed.")
        return False
    else:
        # STUB - log the list of admins here
        log_debug(f"{get_function_name(frame)} successful.")
        return True


def populate_purohit_list() -> bool:
    frame = inspect.currentframe()

    admin_name_col = PUROHIT_WORKSHEET.col_values(1)
    for row_id, cell_value in enumerate(admin_name_col[1:], start=2):
        row_values = PUROHIT_WORKSHEET.row_values(row_id)
        if row_values == []:
            continue
        admin_obj = Member(
            row_values[0], row_values[1], row_values[2]
        )  # REVIEW - Hardcoded, infact the code related to admin is not written according to clean code practices, revist some time later
        PUROHITS.append(admin_obj)

    if len(PUROHITS) == 0:
        log_warning(f"{get_function_name(frame)} unsuccessful.")
        log_warning(f"Fetched zero purohit from the purohit worksheet.")
        log_warning(f"Early termination as atleast one purohit is needed to proceed.")
        return False
    else:
        # STUB - log the list of admins here
        log_debug(f"{get_function_name(frame)} successful.")
        return True


def prepare_data() -> bool:
    """
    Loads the google sheet and initialises the header_to_column mapping.
    """
    frame = inspect.currentframe()

    if load_google_sheet():
        if validate_admin_worksheet_header_integrity():
            if populate_admin_list() and populate_purohit_list():
                if populate_header_to_column_mapping():
                    log_debug(f"{get_function_name(frame)} successful.")
                    return True

    log_error(f"{get_function_name(frame)} unsuccessful.")
    return False


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


def get_todays_recipients() -> list[list[str]]:
    """
    Retrieves processed recipient data for entries registered today.

    Returns:
        list: A list of rows containing recipient data where the registered date matches today's date.
        example : [['1','Ramesh', 'ramesh@email.com'],['19','Suresh', 'suresh@email.com'] ]
    """
    frame = inspect.currentframe()
    log_debug(f"{get_function_name(frame)} called.")

    res = []
    try:
        date_column_values = WORKSHEET.col_values(
            INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_DATE]
        )
        for row_id, cell_value in enumerate(date_column_values[1:], start=2):
            if is_valid_date(cell_value):
                if cell_value[:5] == TODAY[:5]:
                    row_values = WORKSHEET.row_values(row_id)
                    res.append(row_values)

        preprocess_retrived_data(res)
        log_debug(f"{get_function_name(frame)} successful.")
    except Exception as e:
        log_error(f"{get_function_name(frame)} unsuccessful.")
        log_error(f"Exception : {e}")
    return res


def log_todays_recipients(recipients):
    info = "List of recipients : "
    if len(recipients) == 0:
        info += f"Empty."
    else:
        for index, recipient in enumerate(recipients, start=1):
            name = recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_NAME] - 1
            ]
            info += f"{index}.{name}, "
    log_debug(info)


def get_header_row():
    res = []
    for i in range(1, get_num_cols() + 1):
        key = next((k for k, v in INTERNALHEADER_TO_COLUMNID.items() if v == i), None)
        original_name = next(
            (k for k, v in sheetsheader_to_internalreference.items() if v == key), None
        )
        res.append(original_name)
    return res


def save_recipients_as_image(recipients):
    if len(recipients) == 0:
        log_debug(f"Recipient data not saved as image as it is empty.")
        return
    data = recipients.copy()
    header_row = get_header_row()
    data.insert(0, header_row)
    data = np.array(data)

    fig, ax = plt.subplots(figsize=(15, 12))
    table = ax.table(cellText=data, cellLoc="center", loc="center")
    table.auto_set_font_size(True)
    table.auto_set_column_width(col=list(range(len(data[0]))))
    # custom dimensioning
    # table.set_fontsize(8)
    # table.scale(2, 1.3)
    ax.set_axis_off()

    path_to_image = os.path.join(PATH_TEMP_DIR, IMAGE_NAME)
    plt.savefig(path_to_image, dpi=300)
    log_debug(f"Recipient data saved as image at {path_to_image}.")


def save_recipients(recipients) -> bool:
    """
    Log the recipients data and save an image containing list of the recipients
    """
    frame = inspect.currentframe()

    try:
        log_todays_recipients(recipients)
        save_recipients_as_image(recipients)

        log_debug(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        log_error(f"{get_function_name(frame)} unsuccessful.")
        log_error(f"Exception : {e}")
        return False


def get_simple_kannada_message():
    return "ನಿಮ್ಮ ನಾಲೂರು ಶಂಕರ ನಾರಾಯಣ ದೇವರ ಶಾಶ್ವತ ಪೂಜಾ ಸೇವೆ ಇಂದು ನಡೆಯಲಿದೆ"


def get_simple_english_message():
    return "Namaste, your Shashwatha Pooja Seva to Shri Shankara Narayana Swamy was performed today...Regards Temple Trustee, Naloor, Kadaba"


def get_message_for_purohit(recipients):
    return f"Todays Count for Shashwatha Pooja Seva = {len(recipients)}. The list is sent via email."


def get_email_body_for_recipient(title, name):
    return f"""Namasthe dear devotee, {title} {name}. Greetings of the day from Nalur Shankara Narayana Devasthana. Your Shashwatha Pooja Seva is performed today. May the lord Shankara Narayana bless you and your family members. We look forward for your continuous support. \n\n - Temple Committee"""


def get_email_attachement_for_recipient():
    frame = inspect.currentframe()

    res = []
    try:
        standard_image = {}
        standard_image["path"] = os.path.join(PATH_IMAGE_ASSETS_DIR, "standard.jpeg")
        standard_image["name"] = "NalurShankaraNarayana.jpeg"
        res.append(standard_image)
    except Exception as e:
        log_error(f"{get_function_name(frame)} unsuccessful.")
        log_error(f"Exception : {e}")
    return res


def get_email_body_for_purohit(name, recipients):
    html = """\
    <html>
     <head>
        <style>
            p {
                margin: 20px 0; 
            }
            .spacer {
                height: 30px; /* You can adjust this height as needed */
            }
        </style>
    </head>
    """
    html += f"""
    <body>
        <p>ನಮಸ್ತೇ, {name}. ನಾಲೂರು ಶಂಕರ ನಾರಾಯಣ ದೇವಸ್ಥಾನ ಸಮಿತಿಯಿಂದ ದಿನದ ಶುಭಾಶಯಗಳು."</p>
    """

    if len(recipients) == 0:
        html += f"""
        <p>{TODAY} ದಿನಾಂಕದಂದು ಶಾಶ್ವತ ಪೂಜಾ ಸೇವೆ ಇಲ್ಲ.</p>
        <div class="spacer"></div> 
        """
    else:
        html += f"""
        <p>{TODAY} ದಿನಾಂಕದಂದು ಶಾಶ್ವತ ಪೂಜೆಯ ಇಂದಿನ ಸೇವಾ ಕರ್ತರ ವಿವರ.</p>
        """
        include = [
            "Name",
            "Gotra",
            "Nakshatra",
            "Rashi",
        ]
        html += generate_custom_html_table(recipients, get_header_row(), include)
        html += """
        <div class="spacer"></div> 
        """

    html += f"""
    <div class="spacer"></div>
    <div class="spacer"></div>
    <p>- Temple Committee</p>
    </body>
    </html>
    """
    return html


def get_email_body_for_admin(name, recipients):
    html = """\
    <html>
     <head>
        <style>
            p {
                margin: 20px 0; 
            }
            .spacer {
                height: 30px; /* You can adjust this height as needed */
            }
        </style>
    </head>
    """
    html += f"""
    <body>
        <p>Namasthe dear admin, {name}. Greetings of the day from Nalur Shankara Narayana Devasthana.</p>
    """

    if len(recipients) == 0:
        html += f"""
        <p>There is no Shashwatha Pooja Seva today, dated {TODAY}</p>
        """
    else:
        html += f"""
        <p>The following is the list of recipients for today's Shashwatha Pooja Seva, dated {TODAY}.</p>
        """
        html += generate_html_table(recipients, get_header_row())
        html += """
        <div class="spacer"></div> 
        """

    html += f"""
    {"<p>Relevant log file is attached.</p>" if len(recipients) == 0 else "<p>Relevant log file and image are attached</p>"}
    <div class="spacer"></div>
    <div class="spacer"></div>
    <p>- Dev</p>
    </body>
    </html>
    """
    return html


def get_email_attachement_for_admin():
    frame = inspect.currentframe()
    res = []
    try:
        path_to_img = os.path.join(PATH_TEMP_DIR, IMAGE_NAME)
        if os.path.exists(path_to_img):
            recipients_image = {}
            recipients_image["path"] = path_to_img
            recipients_image["name"] = IMAGE_NAME
            res.append(recipients_image)
        log_info_file = {}
        log_info_file["path"] = get_path_to_current_session_log(False)
        log_info_file["name"] = get_path_to_current_session_log(False).split(os.sep)[-1]
        res.append(log_info_file)
        log_debug_file = {}
        log_debug_file["path"] = get_path_to_current_session_log(True)
        log_debug_file["name"] = get_path_to_current_session_log(True).split(os.sep)[-1]
        res.append(log_debug_file)
    except Exception as e:
        log_error(f"{get_function_name(frame)} unsuccessful.")
        log_error(f"Exception : {e}")
    return res


def dispatch_messages_to_recipients(recipients) -> bool:
    """
    Sends confirmation SMS and Email messages to the list of recipients.
    """
    frame = inspect.currentframe()

    try:
        log_debug(f"Dispatching messages to recipients.")
        for recipient in recipients:
            title = recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_TITLE] - 1
            ]
            name = recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_NAME] - 1
            ]
            phone_num = format_phone_number(
                recipient[
                    INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_PHONE_NUMBER] - 1
                ]
            )
            email_address = recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_EMAIL] - 1
            ]
            gotra = recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_GOTRA] - 1
            ]
            rashi = recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_RASHI] - 1
            ]
            nakshatra = recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_NAKSHATRA] - 1
            ]
            language = recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_LANGUAGE] - 1
            ]

            log_debug(
                f"Recipient, Name: {title} {name}, Phone : {phone_num}, Email : {email_address}, Gotra : {gotra}, Rashi : {rashi}, Nakshatra : {nakshatra}."
            )
            if PI_MODE and ENABLE_SMS:
                log_debug(f"Dispatching SMS to {title} {name}.")
                is_kannada = (
                    True if language == "Kannada" and ENABLE_LANGUAGE else False
                )
                simple_message = (
                    get_simple_kannada_message()
                    if is_kannada
                    else get_simple_english_message()
                )
                success_sms = dispatch_sms(phone_num, simple_message, is_kannada)
                if success_sms:
                    log_debug(f"Dispatching SMS to {title} {name} successful.")
                else:
                    log_warning(f"Dispatching SMS to {title} {name} unsuccessful.")
                    # TODO - Add some fail safe mechansim where all unsuccessfull parties are collected and informed to admin

            if ENABLE_EMAIL:
                log_debug(f"Dispatching Email to {title} {name}.")
                subject = "Confirmation : Shashwatha Pooja Seva"
                body = get_email_body_for_recipient(title, name)
                attachments = get_email_attachement_for_recipient()
                success_email = send_email(email_address, subject, body, attachments)
                if success_email:
                    log_debug(f"Dispatching Email to {title} {name} successful.")
                else:
                    log_warning(f"Dispatching Email to {title} {name} unsuccessful.")
                    # TODO - Add some fail safe mechansim where all unsuccessfull parties are collected and informed to admin
            time.sleep(10)
        log_debug(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        log_error(f"{get_function_name(frame)} unsuccessful.")
        log_error(f"Exception : {e}")
        return False


def dispatch_messages_to_purohits(recipients) -> bool:
    """"""
    frame = inspect.currentframe()
    try:
        log_debug(f"Dispatching communications to purohits.")
        for purohit in PUROHITS:
            log_debug(
                f"Purohit, Name: {purohit.name}, Phone : {purohit.phone_number}, Email : {purohit.email}."
            )
            if PI_MODE and ENABLE_SMS:
                log_debug(f"Dispatching SMS to {purohit.name}.")
                message = get_message_for_purohit(recipients)
                success_sms = dispatch_sms(purohit.phone_number, message, False)
                if success_sms:
                    log_debug(f"Dispatching SMS to {purohit.name} successful.")
                else:
                    log_warning(f"Dispatching SMS to {purohit.name} unsuccessful.")
                    # TODO - Add some fail safe mechansim where all unsuccessfull parties are collected and informed to admin
            if ENABLE_EMAIL:
                subject = "Daily Reminder"
                attachments = []
                cc = [admin.email for admin in ADMINS]

                body = get_email_body_for_purohit(purohit.name, recipients)
                send_email(purohit.email, subject, body, attachments, cc, True)
            log_debug(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        log_error(f"{get_function_name(frame)} unsuccessful.")
        log_error(f"Exception : {e}")
        return False


def dispatch_message_to_admins(recipients) -> bool:
    """
    Sends notification email to admins.
    """
    frame = inspect.currentframe()

    try:
        log_debug(f"Dispatching communications to admins.")
        for admin in ADMINS:
            log_debug(
                f"Admin, Name: {admin.name}, Phone : {admin.phone_number}, Email : {admin.email}."
            )
            if ENABLE_EMAIL:
                subject = "Daily Notification"
                attachments = get_email_attachement_for_admin()
                cc = []
                body = get_email_body_for_admin(admin.name, recipients)
                # TODO- get two email body one clean one and one with message saying relay on manual as there are warning
                send_email(admin.email, subject, body, attachments, cc, True)

        log_debug(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        log_error(f"{get_function_name(frame)} unsuccessful.")
        log_error(f"Exception : {e}")
        return False


def perform_cleanup():
    frame = inspect.currentframe()
    if PI_MODE and ENABLE_SMS:
        close_serial()
    log_debug(f"{get_function_name(frame)} successful.")


# TODO - Add a class that validates if the sheet is messed, if the header names are messed, this file and the email to purohit will be messed.
