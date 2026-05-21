from . import *
import inspect


def get_simple_kannada_message():
    return "ನಿಮ್ಮ ನಾಲೂರು ಶಂಕರ ನಾರಾಯಣ ದೇವರ ಶಾಶ್ವತ ಪೂಜಾ ಸೇವೆ ಇಂದು ನಡೆಯಲಿದೆ"


def get_simple_english_message():
    return "On this auspicious day of your Shashwatha Pooja Seva, may Shri Shankara Narayana Swamy bless you and your family with peace and happiness - Naloor, Kadaba"


def get_message_for_purohit(recipients):
    return f"Todays Shashwatha Pooja Sevas = {len(recipients)}. The list is sent via email."


def get_email_body_for_recipient(title, name):
    return f"""Namasthe dear devotee, {title} {name}. Greetings of the day from Nalur Shankara Narayana Devasthana. Your Shashwatha Pooja Seva is performed today. May the lord Shankara Narayana bless you and your family members. We look forward for your continuous support. \n\n - Temple Committee"""


def get_email_body_for_purohit(name, recipients, headers):
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
        <p>ನಮಸ್ತೇ, {name}. ನಾಲೂರು ಶಂಕರ ನಾರಾಯಣ ದೇವಸ್ಥಾನ ಸಮಿತಿಯಿಂದ ದಿನದ ಶುಭಾಶಯಗಳು.</p>
    """

    if len(recipients) == 0:
        html += f"""
        <p>{TODAY} ದಿನಾಂಕದಂದು ಶಾಶ್ವತ ಪೂಜಾ ಸೇವೆ ಇಲ್ಲ.</p>
        <div class="spacer"></div> 
        """
    else:
        html += f"""
        <p>{TODAY} ದಿನಾಂಕದಂದು ಶಾಶ್ವತ ಪೂಜೆಯ ಇಂದಿನ ಸೇವಾಕರ್ತರ ವಿವರ.</p>
        """
        include = [
            "Name",
            "Gotra",
            "Nakshatra",
            "Rashi",
        ]
        html += generate_custom_html_table(recipients, headers, include)
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


def get_email_body_for_admin(name, recipients, headers):
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
        html += generate_html_table(recipients, headers)
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


def get_email_attachement_for_recipient():
    res = []
    try:
        standard_image = {}
        standard_image["path"] = os.path.join(PATH_IMAGE_ASSETS_DIR, "standard.jpeg")
        standard_image["name"] = "NalurShankaraNarayana.jpeg"
        res.append(standard_image)
    except Exception as e:
        frame = inspect.currentframe()
        log_error(f"Exception thrown in {get_function_name(frame)} function.")
        log_error(f"Exception : {e}")
    return res


def get_email_attachement_for_admin(image_name):
    frame = inspect.currentframe()
    res = []
    try:
        path_to_img = os.path.join(PATH_TEMP_DIR, image_name)
        if os.path.exists(path_to_img):
            recipients_image = {}
            recipients_image["path"] = path_to_img
            recipients_image["name"] = image_name
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
