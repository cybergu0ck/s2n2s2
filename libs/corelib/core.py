from . import *
from libs.comslib.email import send_email
from libs.comslib.sms import dispatch_sms, close_serial
from .template import *
import gspread
import time
import inspect
from enum import Enum, auto
import matplotlib.pyplot as plt
import numpy as np

# TODO - Add a class that validates if the sheet is messed, if the header names are messed, this file and the email to purohit will be messed.


WORKSHEET = None
ADMIN_WORKSHEET = None
PUROHIT_WORKSHEET = None
HEADER_ROW = 1
INTERNALHEADER_TO_COLUMNID = {}
ADMINS = []
PUROHITS = []
RECIPIENTS: list | None = None


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


def get_image_name():
    return "recipients-list.png"


def load_google_sheet() -> bool:
    try:
        gc = gspread.service_account()
        sheet = gc.open(SHEETS_TITLE)
        global WORKSHEET
        global ADMIN_WORKSHEET
        global PUROHIT_WORKSHEET
        if DEV_MODE:
            WORKSHEET = sheet.worksheet(WORKSHEET_NAME_DEV_RECIPIENTS)
            ADMIN_WORKSHEET = sheet.worksheet(WORKSHEET_NAME_DEV_ADMINS)
            PUROHIT_WORKSHEET = sheet.worksheet(WORKSHEET_NAME_DEV_PUROHITS)
        else:
            WORKSHEET = sheet.worksheet(WORKSHEET_NAME_PROD_RECIPIENTS)
            ADMIN_WORKSHEET = sheet.worksheet(WORKSHEET_NAME_PROD_ADMINS)
            PUROHIT_WORKSHEET = sheet.worksheet(WORKSHEET_NAME_PROD_PUROHITS)

        log_debug("Successfully loaded data from google sheet.")
        return True
    except Exception as e:
        frame = inspect.currentframe()
        log_warning(f"Exception thrown in {get_function_name(frame)} function.")
        log_warning(f"Exception : {e}")
        return False


def populate_header_to_column_mapping() -> bool:
    """
    Populates a map with keys as internal header references (encoded column headings) and the values as columen id.
    Populates a map with keys as internal header references (encoded column headings) and the values as columen id.
    - This ensures that script will not fail if columns are interchanged or modified.
    - The
    - Example: {nakshatra: 5, rashi : 6}
    """
    try:
        global INTERNALHEADER_TO_COLUMNID
        header_row_values = WORKSHEET.row_values(HEADER_ROW)
        for id, header in enumerate(header_row_values):
            col_id = id + 1
            INTERNALHEADER_TO_COLUMNID[sheetsheader_to_internalreference[header]] = (
                col_id
            )
        log_debug("Successfully mapped header,column.")
        return True
    except Exception as e:
        frame = inspect.currentframe()
        log_warning(f"Exception thrown in {get_function_name(frame)} function.")
        log_warning(f"Exception : {e}")
        log_info(
            f"Check if the header names in the worksheet and in sheetsheader_to_internalreference consistant."
        )
        return False


def validate_admin_worksheet_header_integrity() -> bool:
    header_row = ADMIN_WORKSHEET.row_values(1)
    if header_row == ADMIN_WORKHEET_HEADER_INTEGRITY:
        log_debug("Successfully validated admin worksheet header integrity.")
        return True
    else:
        log_warning("Failure in validating admin worksheet header integrity.")
        return False


def populate_admin_list() -> bool:
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
        ADMINS.append(
            admin_obj
        )  # FIXME - Do not mutate global variables directly, do similar to RECIPIENTS

    if len(ADMINS) == 0:
        log_warning(f"Fetched zero admin from the admin worksheet.")
        return False
    else:
        # STUB - log the list of admins here
        log_debug("Successfully populated admin list.")
        return True


def populate_purohit_list() -> bool:
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
        log_warning(f"Fetched zero purohit from the purohit worksheet.")
        return False
    else:
        # STUB - log the list of admins here
        log_debug("Successfully populated purohit list.")
        return True


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


def load_recipients() -> bool:
    global RECIPIENTS
    frame = inspect.currentframe()
    try:
        recipients = []
        date_column_values = WORKSHEET.col_values(
            INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_DATE]
        )
        for row_id, cell_value in enumerate(date_column_values[1:], start=2):
            if not is_valid_date(cell_value):
                log_warning(f"Invalid date at row {row_id}: {cell_value}")
                continue
            if cell_value[:5] == TODAY[:5]:
                row_values = WORKSHEET.row_values(row_id)
                recipients.append(row_values)

        preprocess_retrived_data(recipients)
        RECIPIENTS = recipients
        return True
    except Exception as e:
        log_error(f"Exception thrown in {get_function_name(frame)}.")
        log_error(f"Exception: {e}")
        RECIPIENTS = []
        return False


def get_todays_recipients() -> list:
    global RECIPIENTS
    if RECIPIENTS is None:
        success = load_recipients()
        if not success:
            return []
    return RECIPIENTS


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
    image_name = get_image_name()
    path_to_image = os.path.join(PATH_TEMP_DIR, image_name)
    plt.savefig(path_to_image, dpi=300)
    log_debug(f"Recipient data saved as image at {path_to_image}.")


def save_recipients(recipients) -> bool:
    """
    Log the recipients data and save an image containing list of the recipients
    """
    try:
        log_todays_recipients(recipients)
        save_recipients_as_image(recipients)
        return True
    except Exception as e:
        frame = inspect.currentframe()
        log_warning(f"Exception thrown in {get_function_name(frame)} function.")
        log_warning(f"Exception : {e}")
        return False


def dispatch_messages_to_recipients(recipients) -> bool:
    """
    Sends SMS and Email to the list of recipients.
    """
    try:
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
            log_debug("\n\n")
            log_debug(
                f"Recipient, Name: {title} {name}, Phone : {phone_num}, Email : {email_address}, Gotra : {gotra}, Rashi : {rashi}, Nakshatra : {nakshatra}."
            )
            if PI_MODE and ENABLE_SMS:
                is_kannada = (
                    True if language == "Kannada" and ENABLE_LANGUAGE else False
                )
                simple_message = (
                    get_simple_kannada_message()
                    if is_kannada
                    else get_simple_english_message()
                )
                if dispatch_sms(phone_num, simple_message, is_kannada):
                    log_debug(
                        f"Successfully sent message to {title} {name} with phone number {phone_num}."
                    )
                else:
                    log_warning(
                        f"Failed to send message to {title} {name} with phone number {phone_num}."
                    )
                    # TODO - Add some fail safe mechansim where all unsuccessfull parties are collected and informed to admin

            if ENABLE_EMAIL:
                subject = "Confirmation : Shashwatha Pooja Seva"
                body = get_email_body_for_recipient(title, name)
                attachments = get_email_attachement_for_recipient()
                if email_address:
                    if send_email(email_address, subject, body, attachments):
                        log_debug(
                            f"Successfully sent email to {title} {name} with email {email_address}."
                        )
                    else:
                        log_warning(
                            f"Failed to send email to {title} {name} with email {email_address}."
                        )
                        # TODO - Add some fail safe mechansim where all unsuccessfull parties are collected and informed to admin
            time.sleep(5)
        log_debug("Successfully dispatched all recipient messages.")
        return True

    except Exception as e:
        frame = inspect.currentframe()
        log_warning(f"Exception thrown in {get_function_name(frame)} function.")
        log_warning(f"Exception : {e}")
        log_warning("Failure in dispatching messages to certain recipients.")
        return False


def dispatch_reminders(recipients) -> bool:
    """
    Send message to purohits and admins
    """
    try:
        for purohit in PUROHITS:
            if PI_MODE and ENABLE_SMS:
                message = get_message_for_purohit(recipients)
                phone_number = format_phone_number(purohit.phone_number)
                if dispatch_sms(phone_number, message, False):
                    log_debug(
                        f"Successfully sent message to {purohit.name} with phone number {phone_number}."
                    )
                else:
                    log_warning(
                        f"Failed to send message to {purohit.name} with phone number {phone_number}."
                    )
                    # TODO - Add some fail safe mechansim where all unsuccessfull parties are collected and informed to admin
            if ENABLE_EMAIL:
                subject = "Daily Reminder"
                attachments = []
                cc = [admin.email for admin in ADMINS]  # NOTE - Admins are CCd
                body = get_email_body_for_purohit(
                    purohit.name, recipients, get_header_row()
                )
                if purohit.email:
                    if send_email(purohit.email, subject, body, attachments, cc, True):
                        log_debug(
                            f"Successfully sent email to {purohit.name} with email {purohit.email}."
                        )
                    else:
                        log_warning(
                            f"Failed to send email to {purohit.name} with email {purohit.email}."
                        )

        for admin in ADMINS:
            if PI_MODE and ENABLE_SMS:
                message = get_message_for_purohit(recipients)  # Intentional
                phone_number = format_phone_number(admin.phone_number)
                if dispatch_sms(phone_number, message, False):
                    log_debug(
                        f"Successfully sent message to {admin.name} with phone number {phone_number}."
                    )
                else:
                    log_warning(
                        f"Failed to send message to {admin.name} with phone number {phone_number}."
                    )
                    # TODO - Add some fail safe mechansim where all unsuccessfull parties are collected and informed to admin
        log_debug("Successfully dispatched necessary reminders.")
        return True

    except Exception as e:
        frame = inspect.currentframe()
        log_warning(f"Exception thrown in {get_function_name(frame)} function.")
        log_warning(f"Exception : {e}")
        log_warning("Failure in dispatching reminders to certain purohits or admins.")
        return False


def setup_environment() -> bool:
    """
    Configure and set up the environment.
    """
    try:
        configure_directories()
        backup_existing_logs()
        configure_logging_system()
        log_debug("Successfully set up the necessary environment.")
        return True
    except Exception as e:
        frame = inspect.currentframe()
        log_warning(f"Exception thrown in {get_function_name(frame)}.")
        log_warning(f"Exception : {e}")
        return False


def process_data():
    """
    Save the data for future email attachements.
    """
    recipients = get_todays_recipients()
    if not save_recipients(recipients):
        log_warning(
            "Failed to process certain data. Recipient image might not be saved."
        )


def fetch_data() -> bool:
    """
    Loads the google sheet and initialises the header_to_column mapping.
    """
    is_success = (
        load_google_sheet()
        and validate_admin_worksheet_header_integrity()
        and populate_admin_list()
        and populate_purohit_list()
        and populate_header_to_column_mapping()
    )

    process_data()

    if is_success:
        log_debug("Successfully fetched necessary data.")
        return True
    else:
        log_warning("Failed to fetch certain necessary data.")
        return False


def dispatch_messages() -> bool:
    """
    Send messages to purohits and recipients.
    """
    recipients = get_todays_recipients()
    are_reminders_successfull = dispatch_reminders(recipients)
    are_messages_successfull = dispatch_messages_to_recipients(recipients)
    if are_reminders_successfull and are_messages_successfull:
        log_debug("Successfully dispatched all communications to relevant parties.")
        return True
    elif are_messages_successfull:
        log_info(
            "Successfully dispatched all communications to recipients but not all admins are reminded."
        )
        return True
    else:
        log_warning("Failure in dispatching reminders and communications.")
        return False


def notify_admins(is_success) -> bool:
    """
    Sends notification email to admins.
    """
    try:
        for admin in ADMINS:
            log_debug("\n\n")
            log_debug(
                f"Admin, Name: {admin.name}, Phone : {admin.phone_number}, Email : {admin.email}."
            )
            if ENABLE_EMAIL:
                subject = "Daily Notification"
                if is_success:
                    if is_info_log_empty():
                        subject += " : " + " Automation Sucess with no warnings."
                    else:
                        subject += " : " + " Automation Sucess with certain warnings."
                else:
                    subject += " : " + " Automation Failure"
                attachments = get_email_attachement_for_admin(get_image_name())
                cc = []
                recipients = get_todays_recipients()
                body = get_email_body_for_admin(
                    admin.name, recipients, get_header_row()
                )
                if admin.email:
                    if send_email(admin.email, subject, body, attachments, cc, True):
                        log_debug(
                            f"Successfully sent email to {admin.name} with email {admin.email}."
                        )
                    else:
                        log_warning(
                            f"Failed to send email to {admin.name} with email {admin.email}."
                        )
        return True

    except Exception as e:
        frame = inspect.currentframe()
        log_error(f"Exception thrown in {get_function_name(frame)} function.")
        log_error(f"Exception : {e}")
        return False


def perform_cleanup():
    if PI_MODE and ENABLE_SMS:
        close_serial()
