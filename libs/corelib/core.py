from . import *
from libs.comslib.email import send_email
from libs.comslib.sms import send_sms_text
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
WORKSHEET = None
ADMIN_WORKSHEET = None
HEADER_ROW = 1
INTERNALHEADER_TO_COLUMNID = {}

IMAGE_NAME = "recipients-list.png"


class Admin:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.phone_number = None
        self.whatsapp_number = None


ADMIN_WORKHEET_HEADER_INTEGRITY = [
    "Name",
    "Email Address",
    "Phone Number",
    "Whatsapp Number",
]

ADMINS = []


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
        log_info(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        print(e)
        log_info(f"{get_function_name(frame)} unsuccessful.")
        log_info(f"Exception : {e}")
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
        log_info(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        print(e)
        log_info(f"{get_function_name(frame)} unsuccessful.")
        log_info(f"Error found in internal header mapping code.")
        log_info(
            f"Check if the header names in the worksheet and in sheetsheader_to_internalreference consistant."
        )
        log_info(f"Exception : {e}")
        return False


def validate_admin_worksheet_header_integrity() -> bool:
    frame = inspect.currentframe()

    header_row = ADMIN_WORKSHEET.row_values(1)
    if header_row == ADMIN_WORKHEET_HEADER_INTEGRITY:
        log_info(f"{get_function_name(frame)} successful.")
        return True
    else:
        log_info(f"{get_function_name(frame)} unsuccessful. ")
        log_info(f"The admin workheet header seems to be modified.")
        return False


def populate_admin_list() -> bool:
    frame = inspect.currentframe()

    admin_name_col = ADMIN_WORKSHEET.col_values(1)
    for row_id, cell_value in enumerate(admin_name_col[1:], start=2):
        row_values = ADMIN_WORKSHEET.row_values(row_id)
        admin_obj = Admin(
            row_values[0], row_values[1]
        )  # REVIEW - Hardcoded, infact the code related to admin is not written according to clean code practices, revist some time later
        ADMINS.append(admin_obj)

    if len(ADMINS) == 0:
        log_info(f"{get_function_name(frame)} unsuccessful.")
        log_info(f"Fetched zero admin from the admin worksheet.")
        log_info(f"Early termination as atleast one admin is needed to proceed.")
        return False
    else:
        # STUB - log the list of admins here
        log_info(f"{get_function_name(frame)} successful.")
        return True


def prepare_data() -> bool:
    """
    Loads the google sheet and initialises the header_to_column mapping.
    """
    frame = inspect.currentframe()

    if load_google_sheet():
        if validate_admin_worksheet_header_integrity():
            if populate_admin_list():
                if populate_header_to_column_mapping():
                    log_info(f"{get_function_name(frame)} successful.")
                    return True

    log_info(f"{get_function_name(frame)} unsuccessful.")
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
    # REVIEW - How to ensure get_todays_recipients is functioning correctly, its the most crucial function call.
    frame = inspect.currentframe()
    log_info(f"{get_function_name(frame)} called.")

    res = []
    date_column_values = WORKSHEET.col_values(
        INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_DATE]
    )
    for row_id, cell_value in enumerate(date_column_values[1:], start=2):
        if is_valid_date(cell_value):
            if cell_value == TODAY:
                row_values = WORKSHEET.row_values(row_id)
                res.append(row_values)

    preprocess_retrived_data(res)
    log_info(f"{get_function_name(frame)} successful.")
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
    log_info(info)


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
        log_info(f"Recipient data not saved as image as it is empty.")
        return
    data = recipients.copy()
    header_row = get_header_row()
    data.insert(0, header_row)
    data = np.array(data)

    fig, ax = plt.subplots(figsize=(14, 10))
    table = ax.table(cellText=data, cellLoc="center", loc="top")
    table.auto_set_font_size(True)
    table.auto_set_column_width(col=list(range(len(data[0]))))
    # custom dimensioning
    # table.set_fontsize(8)
    # table.scale(2, 1.3)
    ax.set_axis_off()

    path_to_image = os.path.join(PATH_TO_TEMP_DIR, IMAGE_NAME)
    plt.savefig(path_to_image, dpi=300)
    log_info(f"Recipient data saved as image at {path_to_image}.")


def save_recipients(recipients) -> bool:
    """
    Log the recipients data and save an image containing list of the recipients
    """
    frame = inspect.currentframe()

    try:
        log_todays_recipients(recipients)
        save_recipients_as_image(recipients)

        log_info(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        print(e)
        log_info(f"{get_function_name(frame)} unsuccessful.")
        return False


def get_simple_message():
    return "Dear devotee of Lord Nalur Shankara Narayana Swamy, your Shashwatha Pooja Seva is performed today."


def get_email_body_for_recipient(title, name):
    return f"""Namasthe dear devotee, {title} {name}. Greetings of the day from Nalur Shankara Narayana Devasthana. Your Shashwatha Pooja Seva is performed today. May the lord Shankara Narayana bless you and your family members. We look forward for your continuous support. \n\n - Temple Committee"""


def get_email_attachement_for_recipient():
    res = []
    standard_image = {}
    standard_image["path"] = os.path.join(PATH_TO_IMAGE_ASSETS_DIR, "standard.jpeg")
    standard_image["name"] = "NalurShankaraNarayana.jpeg"
    res.append(standard_image)
    return res


def get_email_body_for_admin(name, recipients):
    html = """\
    <html>
    """
    html += f"""
    <body>
        <p>Namasthe dear admin, {name}. Greetings of the day from Nalur Shankara Narayana Devasthana.</p>
        <div class="spacer"></div> 
    """

    if len(recipients) == 0:
        html += f"""
        <p>There is no Shashwatha Pooja Seva today, dated {TODAY}</p>
        <div class="spacer"></div> 
        """
    else:
        html += f"""
        <p>The following is the list of recipients for today's Shashwatha Pooja Seva, dated {TODAY}.</p>
        <div class="spacer"></div> 
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
    res = []
    path_to_img = os.path.join(PATH_TO_TEMP_DIR, IMAGE_NAME)
    if os.path.exists(path_to_img):
        recipients_image = {}
        recipients_image["path"] = path_to_img
        recipients_image["name"] = IMAGE_NAME
        res.append(recipients_image)
    log_file = {}
    log_file["path"] = get_path_to_current_session_log(False)
    log_file["name"] = get_path_to_current_session_log(False).split(os.sep)[-1]
    res.append(log_file)
    return res


def dispatch_messages_to_recipients(recipients) -> bool:
    """
    Sends confirmation SMS and Email messages to the list of recipients.
    """
    frame = inspect.currentframe()

    try:
        log_info(f"Dispatching communications to recipients.")
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

            # recipient_info = f"""Following data is fetched for {title} {name} :\n\t\t\t\t\t\t\t\t- Name : {name}\n\t\t\t\t\t\t\t\t- Phone Number : {phone_num}\n\t\t\t\t\t\t\t\t-Email Address : {email_address}\n\t\t\t\t\t\t\t\t- Astrological Info : {gotra}/{rashi}/{nakshatra}"""
            # log_info(recipient_info)

            log_info(
                f"Recipient, Name: {title} {name}, Phone : {phone_num}, Email : {email_address}, Gotra : {gotra}, Rashi : {rashi}, Nakshatra : {nakshatra}."
            )
            simple_message = get_simple_message()
            log_info(f"Dispatching SMS to {title} {name}.")
            if PI_MODE and SMS_ENABLED:
                sucess_sms = send_sms_text(phone_num, simple_message)

            log_info(f"Dispatching Email to {title} {name}.")

            if EMAIL_ENABLED:
                subject = "Confirmation : Shashwatha Pooja Seva"
                body = get_email_body_for_recipient(title, name)
                attachments = get_email_attachement_for_recipient()
                success_email = send_email(email_address, subject, body, attachments)

            time.sleep(3)

        log_info(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        print(e)
        log_info(f"{get_function_name(frame)} unsuccessful.")
        return False


def dispatch_message_to_admins(recipients) -> bool:
    """
    Sends notification email to admins.
    """
    frame = inspect.currentframe()

    try:
        log_info(f"Dispatching communications to admins.")
        for admin in ADMINS:
            log_info(
                f"Admin, Name: {admin.name}, Phone : {admin.phone_number}, Email : {admin.email}."
            )
            if EMAIL_ENABLED:
                subject = "Daily Notification"
                attachments = get_email_attachement_for_admin()
                body = get_email_body_for_admin(admin.name, recipients)
                send_email(admin.email, subject, body, attachments, True)

        log_info(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        print(e)
        log_info(f"{get_function_name(frame)} unsuccessful.")
        log_info(f"Exception : {e}")
        return False


def dispatch_communications(recipients) -> bool:
    frame = inspect.currentframe()

    if dispatch_messages_to_recipients(recipients):
        if dispatch_message_to_admins(recipients):
            log_info(f"{get_function_name(frame)} successful.")
            return True

    log_info(f"{get_function_name(frame)} unsuccessful.")
    return False
