# config.py
import os
import shutil

DEV_MODE = True
PI_MODE = True
ENABLE_SMS = True
ENABLE_EMAIL = True
ENABLE_LANGUAGE = False

DIR_NAME_LOGS = "logs"
DIR_NAME_DEBUG_LOGS = "debug"
DIR_NAME_INFO_LOGS = "info"
LOG_FILE_EXTENSION = ".txt"

PATH_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_LOG_DIR = os.path.join(PATH_ROOT_DIR, DIR_NAME_LOGS)
PATH_DEBUG_LOG_DIR = os.path.join(PATH_LOG_DIR, DIR_NAME_DEBUG_LOGS)
PATH_INFO_LOG_DIR = os.path.join(PATH_LOG_DIR, DIR_NAME_INFO_LOGS)

PATH_ASSETS_DIR = os.path.join(PATH_ROOT_DIR, "assets")
PATH_IMAGE_ASSETS_DIR = os.path.join(PATH_ASSETS_DIR, "images")

DIR_NAME_TEMP = "temp"
PATH_TEMP_DIR = os.path.join(PATH_ROOT_DIR, DIR_NAME_TEMP)

SHEETS_TITLE = "shashwatha-seva-db"
WORKSHEET_NAME_PROD_RECIPIENTS = "prod"
WORKSHEET_NAME_PROD_ADMINS = "admins"
WORKSHEET_NAME_PROD_PUROHITS = "purohits"

WORKSHEET_NAME_DEV_RECIPIENTS = "dev-recipients"
WORKSHEET_NAME_DEV_ADMINS = "dev-admins"
WORKSHEET_NAME_DEV_PUROHITS = "dev-purohits"


def create_log_directories():
    """
    Create directories to store the generated log files if not created already.
    """
    if not os.path.exists(PATH_LOG_DIR):
        os.makedirs(PATH_LOG_DIR)

    if not os.path.exists(PATH_DEBUG_LOG_DIR):
        os.makedirs(PATH_DEBUG_LOG_DIR)

    if not os.path.exists(PATH_INFO_LOG_DIR):
        os.makedirs(PATH_INFO_LOG_DIR)


def create_temp_directory():
    """
    Create a fresh temp directory by destroying if already present.
    """
    if os.path.exists(PATH_TEMP_DIR):
        shutil.rmtree(PATH_TEMP_DIR)
    os.makedirs(PATH_TEMP_DIR)


def configure_directories():
    create_log_directories()
    create_temp_directory()
