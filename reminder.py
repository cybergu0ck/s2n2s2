#!/usr/bin/env python3
"""
This script automates the process of accessing a Google Sheet, parsing its contents, and sending messages to Purohit/Pandit based on the data retrieved. It is designed to run on a Raspberry Pi and is to be scheduled for periodic execution.

This script is intended to be executed in a controlled environment where it can reliably access external resources such as Google Sheets  and email services.
"""
import inspect
from config import configure_directories
from libs.utilslib.utils import *
from libs.loggerlib.logger import (
    configure_logging_system,
    log_info,
    log_error,
    log_debug,
)
from libs.corelib.core import (
    prepare_data,
    get_todays_recipients,
    save_recipients,
    dispatch_messages_to_purohits,
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
        configure_logging_system()
        log_debug(f"{get_function_name(frame)} successful.")
        return True
    except Exception as e:
        print(e)
        log_error(f"{get_function_name(frame)} unsuccessful.")
        return False


def main():
    """Main function to execute the daily messaging script."""
    log_debug("Script started.")
    if setup_environment():
        if prepare_data():
            global RECIPIENTS
            RECIPIENTS = get_todays_recipients()
            if save_recipients(RECIPIENTS):
                if dispatch_messages_to_purohits(RECIPIENTS):
                    log_debug("Reminder script completed successfully.")
                    return
    log_error("Reminder script completed unsuccessfully.")


if __name__ == "__main__":
    main()
    # dispatch_message_to_admins(RECIPIENTS)
    perform_cleanup()
    log_debug("\n\n\n")
