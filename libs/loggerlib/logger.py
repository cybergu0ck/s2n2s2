from . import *

import logging

LOG_DIR_NAME = "logs"
DEV_LOG_DIR_NAME = "dev-logs"
ADMIN_LOG_DIR_NAME = "admin-logs"
DEV_LOG_FILE_EXTENSION = ".txt"
ADMIN_LOG_FILE_EXTENSION = ".doc"
LOGGER = logging.getLogger()


def get_new_filename(filename, is_dev):
    res = increment_filename(filename)
    path = PATH_TO_DEV_LOG_DIR if is_dev else PATH_TO_ADMIN_LOG_DIR
    file_extension = DEV_LOG_FILE_EXTENSION if is_dev else ADMIN_LOG_FILE_EXTENSION
    path_to_new_filename = os.path.join(path, res + file_extension)
    if os.path.exists(path_to_new_filename):
        return get_new_filename(res, is_dev)
    return res


def get_logfile_path(is_dev):
    path = PATH_TO_DEV_LOG_DIR if is_dev else PATH_TO_ADMIN_LOG_DIR
    file_extension = DEV_LOG_FILE_EXTENSION if is_dev else ADMIN_LOG_FILE_EXTENSION
    path_to_log_file = os.path.join(path, f"{TODAY_FOR_LOG}{file_extension}")
    if os.path.exists(path_to_log_file):
        filename = str(os.path.basename(path_to_log_file))
        new_filename = get_new_filename(filename, is_dev)
        path_to_log_file = os.path.join(path, f"{new_filename}{file_extension}")
    return path_to_log_file


def create_log_directories():
    if not os.path.exists(LOG_DIR_NAME):
        os.makedirs(LOG_DIR_NAME)

    global PATH_TO_LOG_DIR
    PATH_TO_LOG_DIR = os.path.join(PATH_TO_ROOT_DIR, LOG_DIR_NAME)

    dev_log_dir = os.path.join(PATH_TO_LOG_DIR, DEV_LOG_DIR_NAME)
    if not os.path.exists(dev_log_dir):
        os.makedirs(f"{LOG_DIR_NAME}/{DEV_LOG_DIR_NAME}")

    global PATH_TO_DEV_LOG_DIR
    PATH_TO_DEV_LOG_DIR = os.path.join(PATH_TO_LOG_DIR, DEV_LOG_DIR_NAME)

    admin_log_dir = os.path.join(PATH_TO_LOG_DIR, ADMIN_LOG_DIR_NAME)
    if not os.path.exists(admin_log_dir):
        os.makedirs(f"{LOG_DIR_NAME}/{ADMIN_LOG_DIR_NAME}")

    global PATH_TO_ADMIN_LOG_DIR
    PATH_TO_ADMIN_LOG_DIR = os.path.join(PATH_TO_LOG_DIR, ADMIN_LOG_DIR_NAME)


def configure_logging_system():
    create_log_directories()

    LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug("Logger configuration successful")

    debug_handler = logging.FileHandler(get_logfile_path(True))
    debug_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    debug_handler.setFormatter(debug_formatter)
    debug_handler.setLevel(logging.DEBUG)
    LOGGER.addHandler(debug_handler)

    info_handler = logging.FileHandler(get_logfile_path(False))
    info_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    info_handler.setFormatter(info_formatter)
    info_handler.setLevel(logging.INFO)
    LOGGER.addHandler(info_handler)
    LOGGER.debug("Logger system configured successfully")
