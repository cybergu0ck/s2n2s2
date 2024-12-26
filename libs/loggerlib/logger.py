from . import *
import logging

LOGGER = logging.getLogger()
PATH_TO_CURRENT_SESSION_DEV_LOG = ""
PATH_TO_CURRENT_SESSION_ADMIN_LOG = ""


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


def configure_logging_system():
    """
    Configures the logging system.
    """

    LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug("Logger configuration successful")
    global PATH_TO_CURRENT_SESSION_DEV_LOG
    PATH_TO_CURRENT_SESSION_DEV_LOG = get_logfile_path(True)
    debug_handler = logging.FileHandler(PATH_TO_CURRENT_SESSION_DEV_LOG)
    debug_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    debug_handler.setFormatter(debug_formatter)
    debug_handler.setLevel(logging.DEBUG)
    LOGGER.addHandler(debug_handler)

    global PATH_TO_CURRENT_SESSION_ADMIN_LOG
    PATH_TO_CURRENT_SESSION_ADMIN_LOG = get_logfile_path(False)
    info_handler = logging.FileHandler(PATH_TO_CURRENT_SESSION_ADMIN_LOG)
    info_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    info_handler.setFormatter(info_formatter)
    info_handler.setLevel(logging.INFO)
    LOGGER.addHandler(info_handler)
    LOGGER.debug("Logger system configured successfully")


def log_info(info):
    LOGGER.info(info)


def log_debug(info):
    LOGGER.debug(info)


def get_path_to_current_session_log(is_dev=False):
    if is_dev:
        return PATH_TO_CURRENT_SESSION_DEV_LOG
    else:
        return PATH_TO_CURRENT_SESSION_ADMIN_LOG
