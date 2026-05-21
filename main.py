#!/usr/bin/env python3
"""
Daily Messaging Automation Workflow

This module orchestrates the automated retrieval, processing, and dispatch of
scheduled communications to purohits, admins and recipients based on Google Sheets data.
Designed for headless deployment, it executes as a periodic cron job.
"""

from libs.utilslib.utils import *
from libs.loggerlib.logger import (
    log_debug,
    log_info,
    log_warning,
    log_error,
)
from libs.corelib.core import (
    setup_environment,
    fetch_data,
    dispatch_messages,
    perform_cleanup,
    notify_admins,
)


def main() -> bool:
    """Execute the daily messaging workflow."""
    is_success = setup_environment() and fetch_data() and dispatch_messages()

    if is_success:
        log_debug("Successfully executed the automation.")
        return True
    else:
        log_error("Failure in Automation.")
        return False


if __name__ == "__main__":
    is_success = main()
    if not notify_admins(is_success):
        log_warning("Failed to notify certain admins")

    log_debug("Notified all admins.")
    perform_cleanup()
    log_debug("End of Script.\n\n\n")
