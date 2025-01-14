from . import *
from datetime import datetime
import re
from re import match

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


def generate_custom_html_table(two_d_array, headers, include):
    """
    Generates a custom HTML table with selected header columns only from a 2D list with styled cells.

    Parameters:
        two_d_array (list of list): A 2D list representing the table two_d_array.

    Returns:
        str: A string containing the HTML representation of the table.
    """
    if len(two_d_array) == 0:
        return "Empty table"
    html = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%; /* Full width */
        }
        th, td {
            border: 1px solid black;
            padding: 20px; /* Increased padding for larger cells */
            text-align: center; /* Center align text */
            min-width: 100px; /* Minimum width for cells */
        }
    </style>
    """
    html += "<table>"
    include_indices = []
    if len(two_d_array[0]) != len(headers):
        html += "  <tr>\n"
        for col_index in range(len(two_d_array[0])):
            html += f"    <th>Column {col_index + 1}</th>\n"
        html += "  </tr>\n"
    else:
        html += "  <tr>\n"
        for i, v in enumerate(headers):
            if v in include:
                include_indices.append(i)
                html += f"    <th>{v}</th>\n"
        html += "  </tr>\n"

    for row in two_d_array:
        html += "  <tr>\n"
        for index in include_indices:
            html += f"    <td>{row[index]}</td>\n"
        html += "  </tr>\n"

    html += "</table>"

    return html


def generate_html_table(two_d_array, headers):
    """
    Generates an HTML table from a 2D list with styled cells for better visibility.

    Parameters:
        two_d_array (list of list): A 2D list representing the table two_d_array.

    Returns:
        str: A string containing the HTML representation of the table.
    """
    if len(two_d_array) == 0:
        return "Empty table"
    html = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%; /* Full width */
        }
        th, td {
            border: 1px solid black;
            padding: 20px; /* Increased padding for larger cells */
            text-align: center; /* Center align text */
            min-width: 100px; /* Minimum width for cells */
        }
    </style>
    """
    html += "<table>"

    if len(two_d_array[0]) != len(headers):
        html += "  <tr>\n"
        for col_index in range(len(two_d_array[0])):
            html += f"    <th>Column {col_index + 1}</th>\n"
        html += "  </tr>\n"
    else:
        headers = headers
        html += "  <tr>\n"
        for header in headers:
            html += f"    <th>{header}</th>\n"
        html += "  </tr>\n"

    for row in two_d_array:
        html += "  <tr>\n"
        for cell in row:
            html += f"    <td>{cell}</td>\n"
        html += "  </tr>\n"

    html += "</table>"

    return html


def is_valid_phone_number(phone_number: str) -> bool:
    """Check if the given string is a valid Indian phone number"""
    pattern = re.compile(r"^\+91\d{10}$")
    if pattern.match(phone_number):
        return True
    else:
        return False


def format_phone_number(phone_number):
    if is_valid_phone_number(phone_number):
        return phone_number
    else:
        res = phone_number
        res.replace(" ", "")
        if match(r"^\d{10}$", res):
            res = "+91" + res
        elif match(r"^91\d{10}$", res):
            res = "+" + res
        return res


def is_valid_email(address: str) -> bool:
    """Check if the given string is a valid email address."""
    return (
        "\n" not in address
        and " " not in address
        and match(
            r"^[a-zA-Z0-9+/=_-]+(\.[a-zA-Z0-9+/=_-]+)*@[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*\.[a-zA-Z]+$",
            address,
        )
    )


def get_function_name(frame):
    return frame.f_code.co_name


def unicode_to_hex(text):
    return "".join(f"{ord(char):04x}" for char in text).upper()
