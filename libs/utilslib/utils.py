from . import *
from datetime import datetime

TODAY = datetime.today().strftime("%d/%m/%Y")
TODAY_FOR_LOG = datetime.today().strftime("%Y-%m-%d")


def increment_filename(filename):
    res = ""
    seperator = "_"
    increment = 0
    filename_without_extension = filename.split(".")[0]
    if len(filename_without_extension.split(seperator)) == 1:
        increment += 1
    else:
        increment = int(filename_without_extension.split(seperator)[-1]) + 1

    res += filename_without_extension.split(seperator)[0] + seperator + str(increment)
    return res


def is_valid_date(value):
    try:
        datetime.strptime(value, "%d/%m/%Y")
        return True
    except (ValueError, TypeError):
        return False
