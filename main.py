#!/usr/bin/env python3
"""
This script automates the process of accessing a Google Sheet, parsing its contents, and sending messages to purohits and recipients based on the data retrieved. It is designed to run on a Raspberry Pi and is to be scheduled for periodic execution.

This script is intended to be executed in a controlled environment where it can reliably access external resources such as Google Sheets  and email services.
"""

import inspect
from config import configure_directories, backup_existing_logs
from libs.utilslib.utils import *
from libs.loggerlib.logger import (
    configure_logging_system,
    log_info,
    log_error,
    log_debug,
)
from libs.corelib.core import (
    fetch_data,
    get_todays_recipients,
    save_recipients,
    dispatch_messages_to_purohits,
    dispatch_messages_to_recipients,
    perform_cleanup,
    dispatch_message_to_admins,
)

RECIPIENTS = None


def setup_environment() -> bool:
    """
    Performs configurations and sets up the environment.
    """
    frame = inspect.currentframe()
    try:
        configure_directories()
        backup_existing_logs()
        configure_logging_system()
        log_debug(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        print(e)
        log_error(f"{get_function_name(frame)} unsuccessful.")
        return False


def main() -> bool:
    """Execute the daily messaging workflow."""
    log_debug("Script started.")

    if not setup_environment():
        log_error("Environment setup failed.")
        return False

    if not fetch_data():
        log_error("Data preparation failed.")
        return False

    recipients = get_todays_recipients()
    if not save_recipients(recipients):
        log_error("Failed to save recipients.")
        return False

    global RECIPIENTS
    RECIPIENTS = recipients

    if dispatch_messages_to_purohits(recipients):
        log_info("Reminders sent successfully.")
    else:
        log_error("Failed to send reminders to purohits.")

    if dispatch_messages_to_recipients(recipients):
        log_info("Messages sent to recipients successfully.")
        return True

    log_error("Failed to send messages to recipients.")
    return False


if __name__ == "__main__":
    success = main()
    dispatch_message_to_admins(RECIPIENTS)
    perform_cleanup()
    log_debug(f"Script ended. success={success}")
    log_debug("\n\n\n")
