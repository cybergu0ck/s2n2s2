from libs.comslib.sms import *

phone_nums = ["+919632448895"]

for i in range(10):
    dispatch_sms(phone_nums[0], "Hello, This is test message")
