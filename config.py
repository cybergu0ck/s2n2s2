# config.py
import os
import shutil

DEV_MODE = True
PI_MODE = True
SMS_ENABLED = True
EMAIL_ENABLED = False

DIR_NAME_LOGS = "logs"
DIR_NAME_DEBUG_LOGS = "debug"
DIR_NAME_INFO_LOGS = "info"
DIR_NAME_ALL_LOGS = "all"
# REVIEW - Decide only one file extension
DEV_LOG_FILE_EXTENSION = ".txt"
ADMIN_LOG_FILE_EXTENSION = ".doc"

PATH_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_LOG_DIR = os.path.join(PATH_ROOT_DIR, DIR_NAME_LOGS)
PATH_DEV_LOG_DIR = os.path.join(PATH_LOG_DIR, DIR_NAME_DEBUG_LOGS)
PATH_ADMIN_LOG_DIR = os.path.join(PATH_LOG_DIR, DIR_NAME_INFO_LOGS)

PATH_ASSETS_DIR = os.path.join(PATH_ROOT_DIR, "assets")
PATH_IMAGE_ASSETS_DIR = os.path.join(PATH_ASSETS_DIR, "images")

DIR_NAME_TEMP = "temp"
PATH_TEMP_DIR = os.path.join(PATH_ROOT_DIR, DIR_NAME_TEMP)


def create_log_directories():
    """
    Create directories to store the generated log files if not created already.
    """
    if not os.path.exists(DIR_NAME_LOGS):
        os.makedirs(DIR_NAME_LOGS)

    if not os.path.exists(PATH_DEV_LOG_DIR):
        os.makedirs(f"{DIR_NAME_LOGS}/{DIR_NAME_DEBUG_LOGS}")

    if not os.path.exists(PATH_ADMIN_LOG_DIR):
        os.makedirs(f"{DIR_NAME_LOGS}/{DIR_NAME_INFO_LOGS}")


def create_temp_directory():
    """
    Create a fresh temp directory by destroying if already present.
    """
    if os.path.exists(PATH_TEMP_DIR):
        shutil.rmtree(PATH_TEMP_DIR)
    os.makedirs(DIR_NAME_TEMP)


def configure_directories():
    create_log_directories()
    create_temp_directory()
