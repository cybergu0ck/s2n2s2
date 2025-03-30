from libs.comslib.sms import *

phone_nums = ["+919632448895"]

for phone_num in phone_nums:
    dispatch_sms(phone_num, "Hello, This is test message")
