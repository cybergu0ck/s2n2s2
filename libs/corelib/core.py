from . import *
from libs.comslib.email import send_email
from libs.comslib.sms import send_sms_text
import gspread
import time

from enum import Enum, auto
import matplotlib.pyplot as plt
import numpy as np
import json

SHEETS_TITLE = "s2n2s2-db"
HEADER_ROW = 1
WORKSHEET = None
INTERNALHEADER_TO_COLUMNID = {}

IMAGE_NAME = "recipients-list.png"


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


def load_google_sheet():
    gc = gspread.service_account()
    sheet = gc.open(SHEETS_TITLE)
    global WORKSHEET
    WORKSHEET = sheet.sheet1


def populate_header_to_column_mapping():
    """
    Populates a map with keys as internal header references (encoded column headings) and the values as columen id.
    Populates a map with keys as internal header references (encoded column headings) and the values as columen id.
    - This ensures that script will not fail if columns are interchanged or modified.
    - The
    - Example: {nakshatra: 5, rashi : 6}
    """
    global INTERNALHEADER_TO_COLUMNID
    header_row_values = WORKSHEET.row_values(HEADER_ROW)
    for id, header in enumerate(header_row_values):
        col_id = id + 1
        INTERNALHEADER_TO_COLUMNID[sheetsheader_to_internalreference[header]] = col_id


def prepare_data():
    """
    Loads the google sheet and initialises the header_to_column mapping.
    """
    load_google_sheet()
    populate_header_to_column_mapping()


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


def get_todays_recepients():
    """
    Retrieves processed recipient data for entries registered today.

    Returns:
        list: A list of rows containing recipient data where the registered date matches today's date.
        example : [['1','Ramesh', 'ramesh@email.com'],['19','Suresh', 'suresh@email.com'] ]
    """
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

    return res


def log_todays_recipients(recipients):
    info = "placeholder text"
    if len(recipients) != 0:
        info = f"""List of recipients:"""
        for recipient in recipients:
            title = recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_TITLE] - 1
            ]
            name = recipient[
                INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_NAME] - 1
            ]
            info += f"\n\t\t\t\t\t\t\t\t- {title} {name}"
    else:
        info = f"List of recipients is empty"
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


def save_recipients(recipients):
    """
    Log the recipients data and save an image containing list of the recipients
    """
    log_todays_recipients(recipients)
    save_recipients_as_image(recipients)


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

    html += """
    <p>The image containing the same data along with the generated log files are attached.</p>
    <div class="spacer"></div>
    <div class="spacer"></div>
    <p>- Dev</p>
    </body>
    </html>
    """
    return html


def get_email_attachement_for_admin():
    res = []
    devotee_image = {}
    devotee_image["path"] = os.path.join(PATH_TO_TEMP_DIR, IMAGE_NAME)
    devotee_image["name"] = IMAGE_NAME
    res.append(devotee_image)
    log_file = {}
    log_file["path"] = get_path_to_current_session_log(False)
    log_file["name"] = get_path_to_current_session_log(False).split(os.sep)[-1]
    res.append(log_file)
    return res


def dispatch_messages_to_recipients(recipients):
    """
    Sends confirmation SMS and email messages to the list of recipients.
    """
    for recipient in recipients:
        title = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_TITLE] - 1]
        name = recipient[INTERNALHEADER_TO_COLUMNID[SheetsHeader.REGISTERED_NAME] - 1]
        phone_num = format_phone_number(
            recipient[
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
            sucess_sms = send_sms_text(phone_num, simple_message)
            if sucess_sms:
                log_info(f"SMS sent successfully to {title} {name}")
            else:
                log_info(f"SMS not sent to {title} {name}")

        log_info(f"Sending email to {title} {name}")

        subject = "Confirmation : Shashwatha Pooja Seva"
        body = get_email_body_for_recipient(title, name)
        attachments = get_email_attachement_for_recipient()
        success_email = send_email(email_address, subject, body, attachments)
        if success_email:
            log_info(f"Email sent successfully to {title} {name}")
        else:
            log_info(f"Email not sent to {title} {name}")

        time.sleep(4)


def dispatch_message_to_admins(recipients):
    """
    Sends notification email to admins.
    """
    path = PATH_TO_ROOT_DIR + os.sep + "users" + os.sep + "users.json"
    with open(path, "r") as file:
        data = json.load(file)
        users = data["users"]
        for user in users:
            if user["admin_privilege"]:
                for email in user["email"]:
                    subject = "Daily Notification"
                    attachments = get_email_attachement_for_admin()
                    body = get_email_body_for_admin(user["name"], recipients)
                    send_email(email, subject, body, attachments, True)
    log_info(f"Email sent successfully to admins")


def dispatch_communications(recipients):
    dispatch_messages_to_recipients(recipients)
    dispatch_message_to_admins(recipients)


def save_and_dispatch(recipients):
    save_recipients(recipients)
    dispatch_communications(recipients)
