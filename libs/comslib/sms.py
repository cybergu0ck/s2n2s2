from . import *
import serial
import time

PORT = "/dev/ttyS0"
BAUD_RATE = 115200
TIME_OUT = 1
LTE_MODULE = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)


def flush_input():
    LTE_MODULE.reset_input_buffer()


def flush_output():
    LTE_MODULE.reset_output_buffer()


def get_service_provider() -> str:
    """Returns the service provider associated with the sim card inserted in the simcom lte module if fetchable else returns empty string."""
    res = ""
    flush_output()
    LTE_MODULE.write(b"AT+CSPN?\r")
    time.sleep(2)
    at_command = LTE_MODULE.readline().decode().strip()
    log_debug(f"AT Command to check service provider: {at_command}")
    response = LTE_MODULE.readline().decode().strip()
    # Successful output will be like '+CSPN: "airtel",0'
    if response.startswith("+CSPN:"):
        res = response.split(",")[0].split(":")[1]
        log_debug(f"Response : {response}")
    else:
        log_warning(f"Unable to fetch service provider detail.")
        log_warning(f"Response : {response}")

    flush_input()
    return res


def get_phone_number() -> str:
    """Returns the phone number associated with the sim card inserted in the simcom lte module if fetchable else returns empty string."""
    # STUB - Add later
    pass


def get_signal_strength() -> str:
    """Returns the signal strength detail if fetchable else returns empty string."""
    res = ""
    flush_output()
    LTE_MODULE.write(b"AT+CSQ\r")
    time.sleep(2)
    at_command = LTE_MODULE.readline().decode().strip()
    log_debug(f"AT Command to check signal strength: {at_command}")
    response = LTE_MODULE.readline().decode().strip()
    # Successful output will be '+CSQ: 22,99'
    if response.startswith("+CSQ:"):
        rssi = response.split(",")[0].split(":")[1]
        try:
            rssi_value = int(rssi)
            if rssi_value > 31:
                res = "Best signal strength."
                log_debug(res)
                log_debug(f"Response : {response}")
            elif rssi_value > 15 and rssi_value < 31:
                res = "Decent signal strength."
                log_debug(res)
                log_debug(f"Response : {response}")
            else:
                res = "Poor signal strength."
                log_warning(res)
                log_warning(f"Response : {response}")
        except Exception as e:
            log_error(f"Error in code.")
            print(f"Exception: {e}")
    else:
        log_warning(f"Unable to fetch network signal strength detail.")
        log_warning(f"Response : {response}")
    flush_input()
    return res


def is_module_functioning() -> bool:
    """Returns True if the simcom lte module is functioning, else False."""
    flush_output()
    res = False
    LTE_MODULE.write(b"AT\r")
    time.sleep(2)
    at_command = LTE_MODULE.readline().decode().strip()
    log_debug(f"AT Command to check if module is functioning : {at_command}")
    response = LTE_MODULE.readline().decode().strip()
    if response == "OK":
        log_debug(f"Response : {response}")
        res = True
    else:
        log_warning(f"Module is not functioning correctly, restart is suggested.")
        log_warning(f"Response : {response}")
        res = False
    flush_input()
    return res


def is_sim_inserted() -> bool:
    """Returns True if sim card is inserted in the simcom lte module, else False."""
    res = False
    flush_output()
    LTE_MODULE.write(b"AT+CIMI\r")
    time.sleep(2)
    at_command = LTE_MODULE.readline().decode().strip()
    log_debug(f"AT Command to check if sim is inserted : {at_command}")
    response_1 = LTE_MODULE.readline().decode().strip()
    response_2 = LTE_MODULE.readline().decode().strip()
    response_3 = LTE_MODULE.readline().decode().strip()
    if response_3 == "OK":
        log_debug(f"Response : {response_1}")
        log_debug(f"Response : {response_2}")
        log_debug(f"Response : {response_3}")
        res = True
    else:
        log_warning(f"Sim not inserted, ensure sim is properly inserted.")
        log_warning(f"Response : {response_1}")
        res = False
    flush_input()
    return res


def is_network_registered() -> bool:
    """Returns True if the simcom lte module is registred to a network, else False."""
    res = False
    flush_output()
    LTE_MODULE.write(b"AT+CREG?\r")
    time.sleep(2)
    at_command = LTE_MODULE.readline().decode().strip()
    log_debug(f"AT Command to check network registration status: {at_command}")
    response_1 = LTE_MODULE.readline().decode().strip()
    response_2 = LTE_MODULE.readline().decode().strip()
    response_3 = LTE_MODULE.readline().decode().strip()
    if response_1.startswith("+CREG:") and response_3 == "OK":
        status = response_1.split(",")[1]
        if status == "0":
            log_warning(
                f" Not registered,ME is not currently searching a new operator to register to."
            )
            log_warning(f"Response : {response_1}")
            res = False
        elif status == "1":
            log_debug(f"Registered to home network.")
            log_debug(f"Response : {response_1}")
            res = True
        elif status == "2":
            log_warning(f"Registered to home network.")
            log_warning(f"Response : {response_1}")
            res = False
        elif status == "3":
            log_warning(f"Registration denied.")
            log_warning(f"Response : {response_1}")
            res = False
        elif status == "4":
            log_warning(f"Unknown response while fetching network registration.")
            log_warning(f"Response : {response_1}")
            res = False
        elif status == "5":
            log_warning(f"Registered, roaming.")
            log_warning(f"Response : {response_1}")
            res = True
        elif status == "6":
            log_warning(f"Registered, sms only.")
            log_warning(f"Response : {response_1}")
            res = True
    else:
        log_warning(f"Unable to fetch network registation detail.")
        log_warning(f"Response : {response_1}")
        res = False
    flush_input()
    return res


def set_sms_message_format(format) -> bool:
    """Sets the sms format, 0 for PDU mode and 1 for Text mode."""
    res = False
    flush_output()
    if format == "0":
        LTE_MODULE.write("AT+CMGF=0\r")
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        log_debug(f"AT Command to set sms message format : {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            log_debug(f"Response : {response}")
            res = True
        else:
            log_warning(f"SMS format not set.")
            log_warning(f"Response : {response}")
            res = False
    elif format == "1":
        LTE_MODULE.write("AT+CMGF=1\r")
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        log_debug(f"AT Command to set sms message format : {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            log_debug(f"Response : {response}")
            res = True
        else:
            log_warning(f"SMS format not set.")
            log_warning(f"Response : {response}")
            res = False
    else:
        log_error(
            "Unsupported sms format. Supported sms format is 0 for PDU mode and 1 for Text mode."
        )
        res = False
    flush_input()
    return res


def set_character_set(character_set: str) -> bool:
    res = False
    flush_output()
    if character_set == "UCS2":
        LTE_MODULE.write(b'AT+CSCS="UCS2"\r')
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        log_debug(f"AT Command to set character set: {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            log_debug(f"Response : {response}")
            res = True
        else:
            log_warning("Character set not set.")
            log_warning(f"Response : {response}")
            res = False
    elif character_set == "IRA":
        LTE_MODULE.write(b'AT+CSCS="IRA"\r')
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        log_debug(f"AT Command to set character set: {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            log_debug(f"Response : {response}")
            res = True
        else:
            log_warning("Character set not set.")
            log_warning(f"Response : {response}")
            res = False
    elif character_set == "GSM":
        LTE_MODULE.write(b'AT+CSCS="GSM"\r')
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        log_debug(f"AT Command to set character set: {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            log_debug(f"Response : {response}")
            res = True
        else:
            log_warning("Character set not set.")
            log_warning(f"Response : {response}")
            res = False
    else:
        log_error(
            "Unsupported character set. Supported character set are IRA, GSM and UCS2."
        )
        res = False
    flush_input()
    return res


def set_text_mode_parameters(is_non_english=False):
    """Set text mode parameters."""
    res = False
    flush_output()
    if is_non_english:
        LTE_MODULE.write(b"AT+CSMP=17,168,0,8\r")
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        log_debug(f"AT Command to set text mode parameters: {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            log_debug(f"Response : {response}")
            res = True
        else:
            log_warning("Text mode parameters not set.")
            log_warning(f"Response : {response}")
            res = False
    else:
        LTE_MODULE.write(b"AT+CSMP=17,168,0,0\r")
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        log_debug(f"AT Command to set text mode parameters: {at_command}")
        response = LTE_MODULE.readline().decode().strip()
        if response == "OK":
            log_debug(f"Response : {response}")
            res = True
        else:
            log_warning("Text mode parameters not set.")
            log_warning(f"Response : {response}")
            res = False
    flush_input()
    return res


def send_sms(phone_number, sms_message, is_hex=False) -> bool:
    res = False
    phone_number = unicode_to_hex(phone_number) if is_hex else phone_number
    sms_message = unicode_to_hex(sms_message) if is_hex else sms_message

    flush_output()
    LTE_MODULE.write(f'AT+CMGS="{phone_number}"\r'.encode())
    time.sleep(2)
    at_command = LTE_MODULE.readline().decode().strip()
    log_debug(f"AT Command to send message : {at_command}")
    response = LTE_MODULE.readline().decode().strip()
    if response == ">":
        LTE_MODULE.write(
            f"{sms_message}\x1A".encode()
        )  # \x1A is the ASCII code for Ctrl+Z
        time.sleep(2)
        at_command = LTE_MODULE.readline().decode().strip()
        log_debug(f"AT Command with message : {at_command}")
        response_1 = LTE_MODULE.readline().decode().strip()
        response_2 = LTE_MODULE.readline().decode().strip()
        response_3 = LTE_MODULE.readline().decode().strip()
        if response_1.startswith("+CMGS:") and response_3 == "OK":
            log_debug(f"Response : {response_1}")
            log_debug(f"Response : {response_2}")
            log_debug(f"Response : {response_3}")
            res = True
        else:
            log_warning(f"Message not sent.")
            log_warning(f"Response : {response_1}")
            res = False
    else:
        log_warning(f"Message not sent.")
        log_warning(f"Response : {response}")
        res = False
    flush_input()
    return res


def close_serial():
    """Close the serial coms"""
    LTE_MODULE.close()


def dispatch_sms(phone_number, sms_message, is_kannada=False) -> bool:
    res = False
    character_set = "UCS2" if is_kannada else "IRA"
    text_mode_parameters = True if is_kannada else False

    if (
        is_valid_phone_number(phone_number)
        and is_module_functioning()
        and is_sim_inserted()
        and is_network_registered()
        and set_character_set(character_set)
        and set_text_mode_parameters(text_mode_parameters)
    ):
        res = send_sms(phone_number, sms_message, is_kannada)
    if res:
        log_debug(
            f"SMS to <{phone_number}> successful using {'kannada' if is_kannada else 'english'}."
        )
    else:
        log_warning(f"SMS to <{phone_number}> unsuccessful.")
    return res


def close_serial():
    LTE_MODULE.close()


# def dispatch_sms(phone_number, sms_message, is_kannada=False) -> bool:
#     res = False
#     if is_valid_phone_number(phone_number):
#         if is_module_functioning():
#             if is_sim_inserted():
#                 if is_network_registered():
#                     if is_kannada:
#                         if set_character_set("UCS2"):
#                             if set_text_mode_parameters(True):
#                                 success = send_sms(phone_number, sms_message, True)
#                                 if success:
#                                     log_debug(
#                                         f"SMS to <{phone_number}> successful using kannada."
#                                     )
#                                     return True
#                                 else:
#                                     log_warning(
#                                         f"SMS to <{phone_number}> unsuccessful."
#                                     )
#                                     return False
#                     else:
#                         if set_character_set("IRA"):
#                             if set_text_mode_parameters(False):
#                                 success = send_sms(phone_number, sms_message, False)
#                                 if success:
#                                     log_debug(
#                                         f"SMS to <{phone_number}> successful using english."
#                                     )
#                                     return True
#                                 else:
#                                     log_warning(
#                                         f"SMS to <{phone_number}> unsuccessful."
#                                     )
#                                     return False
#     log_warning(f"SMS to <{phone_number}> unsuccessful.")
#     return False


# def send_sms_text(recipient_phone_number, sms_message) -> bool:
#     if is_valid_phone_number(recipient_phone_number):
#         LTE_MODULE.write(f'AT+CMGS="{recipient_phone_number}"\r'.encode())
#         time.sleep(2)
#         at_command = LTE_MODULE.readline().decode().strip()
#         log_info(f"AT Command : {at_command}")
#         response = LTE_MODULE.readline().decode().strip()
#         log_info(f"Response : {response}")

#         LTE_MODULE.write(
#             f"{sms_message}\x1A".encode()
#         )  # \x1A is the ASCII code for Ctrl+Z
#         at_command = LTE_MODULE.readline().decode().strip()
#         log_info(f"User command : {at_command}")
#         response = LTE_MODULE.readline().decode().strip()
#         log_info(f"Response : {response}")

#         time.sleep(2)
#         LTE_MODULE.close()
#         log_info(f"SMS to <{recipient_phone_number}> successful.")
#         return True
#     else:
#         log_info(f"SMS to <{recipient_phone_number}> unsuccessful.")
#         log_info(f"Phone number seems to be invalid.")
#         return False
