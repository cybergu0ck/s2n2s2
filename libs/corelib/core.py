from . import *
from enum import Enum, auto

import shutil
import matplotlib.pyplot as plt
import numpy as np

SHEETS_TITLE = "s2n2s2-db"
HEADER_ROW = 1

TEMP_DIR_NAME = "temp"
IMAGE_NAME = "devotee-data.png"


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
    for i in range(1, len(recipients_copy[0]) + 1):
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