from . import *
import serial
import time

PORT = "/dev/ttyS0"
BAUD_RATE = 115200
TIME_OUT = 1

if PI_MODE and ENABLE_SMS:
    global LTE_MODULE
    LTE_MODULE = serial.Serial(PORT, BAUD_RATE, timeout=TIME_OUT)


def close_serial():
    """Close the serial coms"""
    LTE_MODULE.close()


def is_final_response(response):
    if not response:
        return False

    stripped_response = response.strip()
    if stripped_response == "OK":
        return True
    elif stripped_response == "ERROR":
        return True
    elif stripped_response.startswith("+CME ERROR"):
        return True
    elif stripped_response.startswith("+CMS ERROR"):
        return True
    return False


def flush_input():
    LTE_MODULE.reset_input_buffer()


def flush_output():
    LTE_MODULE.reset_output_buffer()


def flush_buffers():
    flush_input()
    flush_output()


def get_service_provider() -> str:
    """Not required for the current usecase."""
    pass


def get_phone_number() -> str:
    """Not required for the current usecase."""
    pass


def get_signal_strength() -> str:
    """Not required for the current usecase."""
    pass


def set_sms_message_format(format) -> bool:
    """Sets the sms format, 0 for PDU mode and 1 for Text mode. Not needed for the current usecase."""
    pass


def reset_module():
    """As per the manual, AT+CRESET resests the module. However when used in minicom it keeps on getting lot of commands about activation and deactivation after receiving OK response. This unpredictable nature will mess up is_final_response logic, hence not implementing this function."""
    pass


def delete_received_sms() -> bool:
    """Deletes all received sms"""
    res = False
    flush_buffers()
    LTE_MODULE.write(f"AT+CMGD=0,4\r".encode())  # at+cmgd=0,4
    time.sleep(0.1)
    at_command = LTE_MODULE.readline().decode().strip()
    log_debug(f"AT Command to send message : {at_command}")
    response = LTE_MODULE.readline().decode().strip()
    if response == "OK":
        log_debug(f"Response : {response}")
        res = True
    else:
        log_warning("Old received messages not deleted.")
        log_warning(f"Response : {response}")
        res = False
    return res


def is_module_functioning() -> bool:
    """
    Returns True if the simcom lte module is functioning, else False.
    AT is the AT command with the following response
      * OK
    """
    res = False
    flush_buffers()

    result_lines = []
    LTE_MODULE.write(b"AT\r")
    line = LTE_MODULE.readline().decode().strip()
    while not is_final_response(line):
        result_lines.append(line)
        print(f"result lines = {result_lines}")
        line = LTE_MODULE.readline().decode().strip()
        print(f"inside while line: {line}")
    result_lines.append(line)
    full_result = "\n".join(result_lines)
    if any("OK" in l for l in result_lines):
        res = True
        log_debug(f"Module is functioning.")
    else:
        log_warning(f"Module is not functioning.")

    return res


def is_sim_inserted() -> bool:
    """
    Returns True if sim card is inserted in the simcom lte module, else False.
    AT+CIMI=? is the AT command with the following responses
      * OK
      * ERROR
    """
    res = True
    flush_buffers()

    result_lines = []
    LTE_MODULE.write(b"AT+CIMI=?\r")
    line = LTE_MODULE.readline().decode().strip()
    while not is_final_response(line):
        result_lines.append(line)
        line = LTE_MODULE.readline().decode().strip()
    result_lines.append(line)
    full_result = "\n".join(result_lines)
    if any("ERROR" in l for l in result_lines):
        res = False
        log_warning(f"Sim not inserted, ensure sim is properly inserted.")
    else:
        log_debug(f"Sim card is detected.")

    return res


def is_network_registered() -> bool:
    """
    Returns True if the simcom lte module is registred to a network, else False.

    AT+CREG? is the AT command with the following responses.
      * +CREG: <n>,<stat>

        OK
      * ERROR
      * +CME ERROR: <err>
    """
    res = True
    flush_buffers()

    result_lines = []
    LTE_MODULE.write(b"AT+CREG?\r")
    line = LTE_MODULE.readline().decode().strip()
    while not is_final_response(line):
        result_lines.append(line)
        line = LTE_MODULE.readline().decode().strip()
    result_lines.append(line)
    full_result = "\n".join(result_lines)
    if any("ERROR" in l or "+CME ERROR" in l for l in result_lines):
        res = False
        log_warning(f"Sim not registered to network.")
    else:
        log_debug(f"Sim is registered to network.")

    return res


def set_character_set(character_set: str) -> bool:
    """
    Set the character set to be used by sim module.
    AT+CSCS=<chset> is the AT command with the following responses.
      * OK
      * ERROR
    """
    res = True
    flush_buffers()

    result_lines = []
    LTE_MODULE.write(f'AT+CSCS="{character_set}"\r'.encode())
    line = LTE_MODULE.readline().decode().strip()
    while not is_final_response(line):
        result_lines.append(line)
        line = LTE_MODULE.readline().decode().strip()
    result_lines.append(line)
    full_result = "\n".join(result_lines)
    if any("ERROR" in l or "+CME ERROR" in l for l in result_lines):
        res = False
        log_warning(f"Failed to set character set for the sim module.")
    else:
        log_debug(f"Succesfull in setting character set.")

    return res


def set_text_mode_parameters(is_non_english=False):
    """
    Set text mode parameters.

    AT+CSMP=<fo>[,<vp>[,<pid>[,<dcs>]]] is the AT command with the following responses
      * OK
      * ERROR
    """
    res = True
    flush_buffers()

    result_lines = []
    cmd = "AT+CSMP=17,168,0,8" if is_non_english else "AT+CSMP=17,168,0,0"
    LTE_MODULE.write((cmd + "\r").encode())
    line = LTE_MODULE.readline().decode().strip()
    while not is_final_response(line):
        result_lines.append(line)
        line = LTE_MODULE.readline().decode().strip()
    result_lines.append(line)
    full_result = "\n".join(result_lines)
    if any("ERROR" in l or "+CME ERROR" in l for l in result_lines):
        res = False
        log_warning(f"Failed to set text mode parameters for the sim module.")
    else:
        log_debug(f"Succesfull in setting text mode parameters.")

    return res


def send_sms(phone_number, sms_message, is_hex=False):
    """
    Send sms to the network.
    AT+CMGS=<da>[,<toda>] is the AT command with the following responses,
      * If sending successfully:
        * +CMGS: <mr>

          OK
      * If cancel sending:
        * OK
      * If sending fails:
        * ERROR
      * If sending fails:
        * +CMS ERROR: <err>
    """
    res = True
    flush_buffers()
    phone_number = unicode_to_hex(phone_number) if is_hex else phone_number
    sms_message = unicode_to_hex(sms_message) if is_hex else sms_message

    result_lines = []
    LTE_MODULE.write(f'AT+CMGS="{phone_number}"\r'.encode())
    LTE_MODULE.write(f"{sms_message}\x1a".encode())
    line = LTE_MODULE.readline().decode().strip()
    while not is_final_response(line):
        result_lines.append(line)
        line = LTE_MODULE.readline().decode().strip()
    result_lines.append(line)
    full_result = "\n".join(result_lines)
    if any("ERROR" in l or "+CMS ERROR" in l for l in result_lines):
        res = False
        log_warning(f"Failed to send sms.")
    else:
        log_debug(f"Succesfull sent sms.")

    return res


def dispatch_sms(phone_number, sms_message, is_kannada=False) -> bool:
    time.sleep(2)
    flush_buffers()
    time.sleep(2)

    res = False
    character_set = "UCS2" if is_kannada else "IRA"
    text_mode_parameters = True if is_kannada else False

    if is_valid_phone_number(phone_number):
        if (
            is_module_functioning()
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
    else:
        log_warning(
            f"SMS to <{phone_number}> unsuccessful because of Invalid phone number."
        )
    log_debug(f"\n\n")
    return res
