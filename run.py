from libs.comslib.sms import *

phone_nums = ["+919632448895"]

for i in range(1):
    dispatch_sms(phone_nums[0], f"Test message {i}")
