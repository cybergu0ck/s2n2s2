from libs.comslib.sms import *
from libs.loggerlib.logger import configure_logging_system
import time

configure_logging_system()

phone_nums = ["+919632448895"]

for i in range(6):
    dispatch_sms(phone_nums[0], f"Test message {i}")
