# config.py
import os
import shutil

DEV_MODE = True
PI_MODE = False

LOG_DIR_NAME = "logs"
DEV_LOG_DIR_NAME = "dev-logs"
ADMIN_LOG_DIR_NAME = "admin-logs"
DEV_LOG_FILE_EXTENSION = ".txt"
ADMIN_LOG_FILE_EXTENSION = ".doc"

PATH_TO_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_TO_LOG_DIR = os.path.join(PATH_TO_ROOT_DIR, LOG_DIR_NAME)
PATH_TO_DEV_LOG_DIR = os.path.join(PATH_TO_LOG_DIR, DEV_LOG_DIR_NAME)
PATH_TO_ADMIN_LOG_DIR = os.path.join(PATH_TO_LOG_DIR, ADMIN_LOG_DIR_NAME)

PATH_TO_ASSETS_DIR = os.path.join(PATH_TO_ROOT_DIR, "assets")
PATH_TO_IMAGE_ASSETS_DIR = os.path.join(PATH_TO_ASSETS_DIR, "images")

TEMP_DIR_NAME = "temp"
PATH_TO_TEMP_DIR = os.path.join(PATH_TO_ROOT_DIR, TEMP_DIR_NAME)


def create_log_directories():
    """
    Create directories to store the generated log files if not created already.
    """
    if not os.path.exists(LOG_DIR_NAME):
        os.makedirs(LOG_DIR_NAME)

    if not os.path.exists(PATH_TO_DEV_LOG_DIR):
        os.makedirs(f"{LOG_DIR_NAME}/{DEV_LOG_DIR_NAME}")

    if not os.path.exists(PATH_TO_ADMIN_LOG_DIR):
        os.makedirs(f"{LOG_DIR_NAME}/{ADMIN_LOG_DIR_NAME}")


def create_temp_directory():
    """
    Create a fresh temp directory by destroying if already present.
    """
    if os.path.exists(PATH_TO_TEMP_DIR):
        shutil.rmtree(PATH_TO_TEMP_DIR)
    os.makedirs(TEMP_DIR_NAME)


def configure_directories():
    create_log_directories()
    create_temp_directory()
