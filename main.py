#!/usr/bin/env python3
"""
This script automates the process of accessing a Google Sheet, parsing its contents, and sending messages to recipients based on the data retrieved. It is designed to run on a Raspberry Pi and is to be scheduled for periodic execution.

This script is intended to be executed in a controlled environment where it can reliably access external resources such as Google Sheets  and email services.
"""

from config import configure_directories
from libs.utilslib.utils import *
from libs.loggerlib.logger import configure_logging_system, log_info
from libs.corelib.core import (
    prepare_data,
    get_todays_recepients,
    save_and_dispatch,
)


def setup_environment():
    """
    Performs configurations and sets up the environment.
    """
    configure_directories()
    configure_logging_system()


def main():
    """Main function to execute the daily messaging script."""
    log_info("Starting todays script execution")
    setup_environment()
    prepare_data()
    recipients = get_todays_recepients()
    save_and_dispatch(recipients)
    log_info("Script executed completely")


if __name__ == "__main__":
    main()
