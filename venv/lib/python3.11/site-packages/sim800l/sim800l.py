#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#############################################################################
# Driver for SIM800L module (using AT commands)
# Tested on Raspberry Pi
# Based on https://github.com/jakhax/raspberry-pi-sim800l-gsm-module (marked
# as "legacy code" where not yet improved) with many enhancements.
#############################################################################

"""
- python3.7/python3.9 (tested with these versions)
sudo apt-get update
sudo apt-get -y upgrade
python3 -m pip install --upgrade pip
pip3 install pyserial
pip3 install gsm0338
"""

import os
import time
import sys
import traceback
import serial
import re
import logging
from datetime import datetime
import subprocess
import termios
import tty
import gsm0338
import zlib
try:
    from RPi import GPIO
except ModuleNotFoundError:
    GPIO = None

httpaction_method = {
    "0": "GET",
    "1": "PUT",
    "2": "HEAD",
    "3": "DELETE",
    "X": "Unknown"
}

httpaction_status_codes = {
    "000": "Unknown HTTPACTION error",
    "100": "Continue",
    "101": "Switching Protocols",
    "200": "OK",
    "201": "Created",
    "202": "Accepted",
    "203": "Non-Authoritative Information",
    "204": "No Content",
    "205": "Reset Content",
    "206": "Partial Content",
    "300": "Multiple Choices",
    "301": "Moved Permanently",
    "302": "Found",
    "303": "See Other",
    "304": "Not Modified",
    "305": "Use Proxy",
    "307": "Temporary Redirect",
    "400": "Bad Request",
    "401": "Unauthorized",
    "402": "Payment Required",
    "403": "Forbidden",
    "404": "Not Found",
    "405": "Method Not Allowed",
    "406": "Not Acceptable",
    "407": "Proxy Authentication Required",
    "408": "Request Time-out",
    "409": "Conflict",
    "410": "Gone",
    "411": "Length Required",
    "412": "Precondition Failed",
    "413": "Request Entity Too Large",
    "414": "Request-URI Too Large",
    "415": "Unsupported Media Type",
    "416": "Requested range not satisfiable",
    "417": "Expectation Failed",
    "500": "Internal Server Error",
    "501": "Not Implemented",
    "502": "Bad Gateway",
    "503": "Service Unavailable",
    "504": "Gateway Time-out",
    "505": "HTTP Version not supported",
    "600": "Not HTTP PDU",
    "601": "Network Error",
    "602": "No memory",
    "603": "DNS Error",
    "604": "Stack Busy",
    "605": "SSL failed to establish channels",
    "606": "SSL fatal alert message with immediate connection termination"
}


def convert_to_string(buf):
    """
    Convert gsm03.38 bytes to string
    :param buf: gsm03.38 bytes
    :return: UTF8 string
    """
    return buf.decode('gsm03.38', errors="ignore").strip()


def convert_gsm(string):
    """
    Encode the string with 3GPP TS 23.038 / ETSI GSM 03.38 codec.
    :param string: UTF8 string
    :return: gsm03.38 bytes
    """
    return string.encode("gsm03.38")


class SIM800L:
    """
    Main class
    """

    def __init__(self, port="/dev/serial0", baudrate=115000, timeout=3.0):
        """
        SIM800L Class constructor
        :param port: port name
        :param baudrate: baudrate in bps
        :param timeout: timeout in seconds
        """
        self.ser = None
        try:
            self.ser = serial.Serial(
                port=port, baudrate=baudrate, timeout=timeout)
        except serial.SerialException as e:
            # traceback.print_exc(file = sys.stdout)
            # logging.debug(traceback.format_exc())
            logging.critical("SIM800L - Error opening GSM serial port - %s", e)
            return

        fd = self.ser.fileno()
        attr = termios.tcgetattr(fd)
        attr[3] &= ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, attr)
        tty.setraw(fd)

        self.incoming_action = None
        self.no_carrier_action = None
        self.clip_action = None
        self._clip = None
        self.msg_action = None
        self._msgid = 0
        self.savbuf = None

    def check_sim(self):
        """
        Check whether the SIM card has been inserted.
        :return: True if the SIM is inserted, otherwise False; None in case
            of module error.
        """
        sim = self.command_data_ok('AT+CSMINS?')
        if not sim:
            return None
        return re.sub(r'\+CSMINS: \d*,(\d*).*', r'\1', sim) == '1'

    def get_date(self):
        """
        Return the clock date available in the module
        :return: datetime.datetime; None in case of module error.
        """
        date_string = self.command_data_ok('AT+CCLK?')
        if not date_string:
            return None
        logging.debug("SIM800L - date_string: %s", date_string)
        date = re.sub(r'.*"(\d*/\d*/\d*,\d*:\d*:\d*).*', r"\1", date_string)
        logging.debug("SIM800L - date: %s", date)
        return datetime.strptime(date, '%y/%m/%d,%H:%M:%S')

    def is_registered(self):
        """
        Check whether the SIM is Registered, home network
        :return: Truse if registered, otherwise False; None in case of module
            error.
        """
        reg = self.command_data_ok('AT+CREG?')
        if not reg:
            return None
        registered = re.sub(r'^\+CREG: (\d*),(\d*)$', r"\2", reg)
        if registered == "1" or registered == "5":
            return True
        return False

    def get_operator(self):
        """
        Display the current network operator that the handset is currently
        registered with.
        :return: operator string; False in case of SIM error. None in case of
            module error.
        """
        operator_string = self.command_data_ok('AT+COPS?')
        operator = re.sub(r'.*"(.*)".*', r'\1', operator_string).capitalize()
        if operator.startswith("+COPS: 0"):
            return False
        return operator

    def get_operator_list(self):
        """
        Display a full list of network operator names.
        :return: dictionary of "numeric: "name" fields; None in case of error.
        """
        ret = {}
        operator_string = self.command('AT+COPN\n', lines=0)
        expire = time.monotonic() + 60  # seconds
        while time.monotonic() < expire:
            r = self.check_incoming()
            if not r:
                return None
            if r == ("OK", None):
                break
            if r == ('GENERIC', None):
                continue
            if r[0] != "COPN":
                logging.error("SIM800L - wrong return message: %s", r)
                return None
            ret[r[1]] = r[2]
        return ret

    def get_service_provider(self):
        """
        Get the Get Service Provider Name stored inside the SIM
        :return: string; None in case of module error. False in case of
            SIM error. 
        """
        sprov_string = self.command_data_ok('AT+CSPN?')
        if not sprov_string:
            return None
        if sprov_string == "ERROR":
            return False
        sprov = re.sub(r'.*"(.*)".*', r'\1', sprov_string)
        return sprov

    def get_battery_voltage(self):
        """
        Return the battery voltage in Volts
        :return: floating (volts). None in case of module error.
        """
        battery_string = self.command_data_ok('AT+CBC')
        if not battery_string:
            return None
        battery = re.sub(r'\+CBC: \d*,\d*,(\d*)', r'\1', battery_string)
        return int(battery) / 1000

    def get_msisdn(self):
        """
        Get the MSISDN subscriber number
        :return: string;  None in case of module error.
        """
        msisdn_string = self.command('AT+CNUM\n')
        if not msisdn_string:
            return None
        r = self.check_incoming()
        if msisdn_string == "OK":
            return "Unstored MSISDN"
        if r != ("OK", None):
            logging.error("SIM800L - wrong return message: %s", r)
            return None
        msisdn = re.sub(r'.*","([+0-9][0-9]*)",.*', r'\1', msisdn_string)
        return msisdn

    def get_signal_strength(self):
        """
        Get the signal strength
        :return: number; min = 3, max = 100; None in case of module error.
        """
        signal_string = self.command_data_ok('AT+CSQ')
        if not signal_string:
            return None
        signal = int(re.sub(r'\+CSQ: (\d*),.*', r'\1', signal_string))
        if signal == 99:
            return 0
        return (signal + 1) / 0.32  # min = 3, max = 100

    def get_unit_name(self):
        """
        Get the SIM800 GSM module unit name
        :return: string; None in case of module error.
        """
        return self.command_data_ok('ATI')

    def get_hw_revision(self, method=0):
        """
        Get the SIM800 GSM module hw revision
        :return: string; None in case of module error.
        """
        if method == 2:
            return self.command_data_ok('AT+GMR')
        firmware = self.command_data_ok('AT+CGMR')
        if not firmware:
            return None
        if method == 1:
            logging.info("Firmware version: R%s.%s",
                firmware[9:11], firmware[11:13])
            logging.info("Device: %s", firmware[16:23])
            logging.info("Rel: %s", firmware[13:16])
            logging.info("Hardware Model type: %s", firmware[23:])
        return firmware

    def get_serial_number(self):
        """
        Get the SIM800 GSM module serial number
        :return: string; None in case of module error.
        """
        return self.command_data_ok('AT+CGSN')

    def get_ccid(self):
        """
        Get the ICCID
        :return: string; None in case of module error.
        """
        return self.command_data_ok('AT+CCID')

    def get_imsi(self):
        """
        Get the IMSI
        :return: string; None in case of module error.
        """
        return self.command_data_ok('AT+CIMI')

    def get_temperature(self):
        """
        Get the SIM800 GSM module temperature in Celsius degrees
        :return: string; None in case of module error.
        """
        temp_string = self.command_data_ok('AT+CMTE?')
        if not temp_string:
            return None
        temp = re.sub(r'\+CMTE: \d*,([0-9.]*).*', r'\1', temp_string)
        return temp

    def get_flash_id(self):
        """
        Get the SIM800 GSM module flash ID
        :return: string; None in case of module error.
        """
        return self.command_data_ok('AT+CDEVICE?')

    def set_date(self):
        """
        Set the Linux system date with the GSM time
        :return: date string; None in case of module error.
        """
        date = self.get_date()
        if not date:
            return None
        date_string = date.strftime('%c')
        with subprocess.Popen(
                ["sudo", "date", "-s", date_string],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT) as sudodate:
            sudodate.communicate()
        return date

    def setup(self):
        """
        Run setup strings for the initial configuration of the SIM800 module
        :return: True if setup is completed; None in case of module error.
        """
        if self.command('ATE0;+IFC=1,1\n') != 'OK':
            return None
        # ATE0        -> command echo off
        # AT+IFC=1,1  -> use XON/XOFF
        if (self.command(
            'AT+CLIP=1;+CMGF=1;+CLTS=1;+CSCLK=0;+CSCS="GSM";+CMGHEX=1\n')
            != 'OK'):
            return None
        # AT+CLIP=1     -> caller line identification
        # AT+CMGF=1     -> plain text SMS
        # AT+CLTS=1     -> enable get local timestamp mode
        # AT+CSCLK=0    -> disable automatic sleep
        # AT+CSCS="GSM" -> Use GSM char set
        # AT+CMGHEX=1   -> Enable or Disable Sending Non-ASCII Character SMS
        return True

    def callback_incoming(self, action):
        self.incoming_action = action

    def callback_no_carrier(self, action):
        self.no_carrier_action = action

    def get_clip(self):
        """
        Not used
        """
        return self._clip

    def callback_msg(self, action):
        self.msg_action = action

    def get_msgid(self):
        """
        Return the unsolicited notification of incoming SMS
        :return: number
        """
        return self._msgid

    def set_charset_hex(self):
        """
        Set HEX character set (only hexadecimal values from 00 to FF)
        :return: "OK" if successful, otherwise None
        """
        return self.command_ok('AT+CSCS="HEX"')

    def set_charset_ira(self):
        """
        Set the International reference alphabet (ITU-T T.50) character set
        :return: "OK" if successful, otherwise None
        """
        return self.command_ok('AT+CSCS="IRA"')

    def hard_reset(self, reset_gpio):
        """
        This function can only be used on a Raspberry Pi.
        Perform a hard reset of the SIM800 module through the RESET pin
        :param reset_gpio: RESET pin
        :return: True if the SIM is active after the reset, otherwise False
            None in case of module error.
        """
        if not GPIO:
            logging.critical("SIM800L - hard_reset() function not available")
            return None
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(reset_gpio, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.output(reset_gpio, GPIO.HIGH)
        GPIO.output(reset_gpio, GPIO.LOW)
        time.sleep(0.3)
        GPIO.output(reset_gpio, GPIO.HIGH)
        time.sleep(7)
        return self.check_sim()

    def serial_port(self):
        """
        Return the serial port (for direct debugging)
        :return:
        """
        return self.ser

    def send_sms(self, destno, msgtext):
        """
        Send SMS message
        :param destno: MSISDN destination number
        :param msgtext: Text message
        :return: 'OK' if message is sent, otherwise 'ERROR'
        """
        result = self.command('AT+CMGS="{}"\n'.format(destno),
                              lines=99,
                              waitfor=5000, # it means 4 seconds
                              msgtext=msgtext)
        self.check_incoming()
        if result and result == '>' and self.savbuf:
            params = self.savbuf.split(':')
            if params[0] == '+CUSD' or params[0] == '+CMGS':
                return True
        return False

    def read_sms(self, index_id):
        """
        Read the SMS message referred to the index
        :param index_id: index in the SMS message list starting from 1
        :return: None if error, otherwise return a tuple including:
                MSISDN origin number, SMS date string, SMS time string, SMS text
        """
        result = self.command('AT+CMGR={}\n'.format(index_id), lines=99)
        self.check_incoming()
        if result:
            params = result.split(',')
            if not params[0] == '':
                params2 = params[0].split(':')
                if params2[0] == '+CMGR':
                    number = params[1].replace('"', '').strip()
                    date = params[3].replace('"', '').strip()
                    msg_time = params[4].replace('"', '').strip()
                    return [number, date, msg_time, self.savbuf]
        return None

    def delete_sms(self, index_id):
        """
        Delete the SMS message referred to the index
        :param index_id: index in the SMS message list starting from 1
        :return: None
        """
        self.command('AT+CMGD={}\n'.format(index_id), lines=1)
        self.check_incoming()

    def get_ip(self):
        """
        Get the IP address of the PDP context
        :return: valid IP address string if the bearer is connected,
            otherwise `None`
        """
        ip_address = None
        r = self.command('AT+SAPBR=2,1\n', lines=0)
        expire = time.monotonic() + 2  # seconds
        s = self.check_incoming()
        ip_address = None
        while time.monotonic() < expire:
            if s[0] == 'IP':
                ip_address = s[1]
                break
            time.sleep(0.1)
            s = self.check_incoming()
        if self.check_incoming() != ('OK', None):
            logging.debug(
                "SIM800L - missing OK message while getting the IP address.")
            return None
        if not ip_address or ip_address == '0.0.0.0':
            logging.debug("SIM800L - NO IP Address")
            return None
        logging.debug("SIM800L - Returned IP Address: %s", ip_address)
        return ip_address

    def disconnect_gprs(self, apn=None):
        """
        Disconnect the bearer.
        :return: True if succesfull, False if error
        """
        return self.command_ok('AT+SAPBR=0,1')

    def connect_gprs(self, apn=None):
        """
        Connect to the bearer and get the IP address of the PDP context.
        Automatically perform the full PDP context setup.
        Reuse the IP session if an IP address is found active.
        :param apn: APN name
        :return: False if error, otherwise return the IP address (as string)
        """
        if apn is None:
            logging.critical("Missing APN name")
            return False
        ip_address = self.get_ip()
        if ip_address is False:
            return False
        if ip_address:
            logging.info("SIM800L - Already connected: %s", ip_address)
        else:
            r = self.command_ok(
                'AT+SAPBR=3,1,"CONTYPE","GPRS";+SAPBR=3,1,"APN","' +
                apn + '";+SAPBR=1,1',
                check_error=True)
            if r == "ERROR":
                logging.critical("SIM800L - Cannot connect to GPRS")
                return False
            if not r:
                return False
            ip_address = self.get_ip()
            if not ip_address:
                logging.error("SIM800L - Cannot connect bearer")
                return False
            logging.debug("SIM800L - Bearer connected")
        return ip_address

    def query_ip_address(self,
            url=None,
            apn=None,
            http_timeout=10,
            keep_session=False):
        """
        Connect to the bearer, get the IP address and query an internet domain
        name, getting the IP address.
        Automatically perform the full PDP context setup.
        Disconnect the bearer at the end (unless keep_session = True)
        Reuse the IP session if an IP address is found active.
        :param url: internet domain name to be queried
        :param http_timeout: timeout in seconds
        :param keep_session: True to keep the PDP context active at the end
        :return: False if error, otherwise the returned IP address (string)
        """
        if not url:
            logging.error("SIM800L - missing URL parameter")
            return False
        ip_address = self.connect_gprs(apn=apn)
        r = self.command('AT+CIFSR\n')
        if not r:
            return None
        if r == 'ERROR':
            if ip_address is False:
                if not keep_session:
                    self.disconnect_gprs()
                return False
            if not self.command_ok('AT+CSTT="' + apn + '";+CIICR'):
                self.command('AT+CIPSHUT\n')
                if not keep_session:
                    self.disconnect_gprs()
                return False
        logging.info("SIM800L - IP Address: %s", self.command('AT+CIFSR\n'))
        cmd = 'AT+CDNSGIP="' + url + '"'
        if not self.command_ok(cmd):
            logging.error("SIM800L - error while querying DNS")
            self.command('AT+CIPSHUT\n')
            if not keep_session:
                self.disconnect_gprs()
            return False
        expire = time.monotonic() + http_timeout
        s = self.check_incoming()
        if not s:
            return None
        dns = False
        while time.monotonic() < expire:
            if s[0] == 'DNS':
                if not s[1]:
                    logging.error(
                        "SIM800L - error while querying DNS: %s", s[2])
                    self.command('AT+CIPSHUT\n')
                    if not keep_session:
                        self.disconnect_gprs()
                    return False
                dns = s[1]
                logging.info("DNS: %s", dns)
                break
            time.sleep(0.1)
            s = self.check_incoming()
            if not s:
                return None
        self.command('AT+CIPSHUT\n')
        if not keep_session:
            self.disconnect_gprs()
        return dns

    def internet_sync_time(self,
            time_server="193.204.114.232",  # INRiM NTP server
            time_zone_quarter=4,  # 1/4 = UTC+1
            apn=None,
            http_timeout=10,
            keep_session=False):
        """
        Connect to the bearer, get the IP address and sync the internal RTC with
        the local time returned by the NTP time server (Network Time Protocol).
        Automatically perform the full PDP context setup.
        Disconnect the bearer at the end (unless keep_session = True)
        Reuse the IP session if an IP address is found active.
        :param time_server: internet time server (IP address string)
        :param time_zone_quarter: time zone in quarter of hour
        :param http_timeout: timeout in seconds
        :param keep_session: True to keep the PDP context active at the end
        :return: False if error, otherwise the returned date (datetime.datetime)
        """
        ip_address = self.connect_gprs(apn=apn)
        if ip_address is False:
            if not keep_session:
                self.disconnect_gprs()
            return False
        cmd = 'AT+CNTP="' + time_server + '",' + str(time_zone_quarter)
        if not self.command_ok(cmd):
            logging.error("SIM800L - sync time did not return OK.")
        if not self.command_ok('AT+CNTP'):
            logging.error("SIM800L - AT+CNTP did not return OK.")
        expire = time.monotonic() + http_timeout
        s = self.check_incoming()
        ret = False
        while time.monotonic() < expire:
            if s[0] == 'NTP':
                if not s[1]:
                    logging.error("SIM800L - Sync time error %s", s[2])
                    if not keep_session:
                        self.disconnect_gprs()
                    return False
                ret = True
                break
            time.sleep(0.1)
            s = self.check_incoming()
        if ret:
            logging.debug("SIM800L - Network time sync successful")
            ret = self.get_date()
        if not keep_session:
            self.disconnect_gprs()
        return ret

    def http(self,
             url=None,
             data=None,
             apn=None,
             method=None,
             use_ssl=False,
             ua=None,
             content_type="application/json",
             allow_redirection=False,
             http_timeout=10,
             keep_session=False):
        """
        Run the HTTP GET method or the HTTP PUT method and return retrieved data
        Automatically perform the full PDP context setup and close it at the end
        (use keep_session=True to keep the IP session active). Reuse the IP
        session if an IP address is found active.
        Automatically open and close the HTTP session, resetting errors.
        :param url: URL
        :param data: input data used for the PUT method (bytes)
        :param apn: APN name
        :param method: GET or PUT
        :param use_ssl: True if using HTTPS, False if using HTTP; note:
            The SIM800L module only supports  SSL2, SSL3 and TLS 1.0.
        :param ua: User agent (string); is not set, the SIM800L default user
            agent is used ("SIMCom_MODULE").
        :param content_type: (string) set the "Content-Type" field in the HTTP
            header.
        :param allow_redirection: True if HTTP redirection is allowed (e.g., if
            the server sends a redirect code (range 30x), the client will
            automatically send a new HTTP request)
        :param http_timeout: timeout in seconds
        :param keep_session: True to keep the PDP context active at the end
        :return: False if error, otherwise the returned data (as string)
        """
        if url is None:
            logging.critical("Missing HTTP url")
            return False
        if method is None:
            logging.critical("Missing HTTP method")
            return False
        ip_address = self.connect_gprs(apn=apn)
        if ip_address is False:
            if not keep_session:
                self.disconnect_gprs()
            return False
        allow_redirection_string = ';+HTTPPARA="REDIR",0'
        if allow_redirection:
            allow_redirection_string = ';+HTTPPARA="REDIR",1'
        use_ssl_string = ';+HTTPSSL=0'
        if use_ssl:
            use_ssl_string = ';+SSLOPT=0,0;+HTTPSSL=1'
        if ua:
            ua_string = ';+HTTPPARA="UA","' + ua + '"'
        else:
            ua_string = ""
        cmd = ('AT+HTTPINIT;'
                '+HTTPPARA="CID",1'
                ';+HTTPPARA="URL","' + url + '"' + ua_string +
                ';+HTTPPARA="CONTENT","' + content_type + '"' +
                allow_redirection_string +
                use_ssl_string)  # PUT
        if method == "GET":
            cmd = ('AT+HTTPINIT;+HTTPPARA="CID",1;+HTTPPARA="URL","' + url + '"'
                + allow_redirection_string +
                use_ssl_string)  # GET
        r = self.command_ok(cmd)
        if not r:
            self.command('AT+HTTPTERM\n')
            r = self.command_ok(cmd)
            if not r:
                if not keep_session:
                    self.disconnect_gprs()
                return False
        r = self.command_ok('AT+IFC=0,0')  # disable flow contol
        if not r:
            self.command('AT+HTTPTERM\n')
            r = self.command_ok(cmd)
            if not r:
                if not keep_session:
                    self.disconnect_gprs()
                return False
        if method == "PUT":
            if not data:
                logging.critical("SIM800L - Null data paramether.")
                self.command('AT+HTTPTERM\n')
                if not keep_session:
                    self.disconnect_gprs()
                return False
            len_input = len(data)
            cmd = 'AT+HTTPDATA=' + str(len_input) + ',' + str(
                http_timeout * 1000)
            r = self.command_ok(cmd, check_download=True, check_error=True)
            if r == "ERROR":
                logging.critical("SIM800L - AT+HTTPDATA returned ERROR.")
                self.command('AT+HTTPTERM\n')
                if not keep_session:
                    self.disconnect_gprs()
                return False
            if r != "DOWNLOAD":
                logging.critical(
                    "SIM800L - Missing 'DOWNLOAD' return message: %s", r)
                self.command('AT+HTTPTERM\n')
                if not keep_session:
                    self.disconnect_gprs()
                return False
            logging.debug("SIM800L - Writing data; length = %s", len_input)
            self.ser.write(data + '\n'.encode())
            expire = time.monotonic() + http_timeout
            s = self.check_incoming()
            while s == ('GENERIC', None) and time.monotonic() < expire:
                time.sleep(0.1)
                s = self.check_incoming()
            if s != ("OK", None):
                self.command('AT+HTTPTERM\n')
                if not keep_session:
                    self.disconnect_gprs()
                return False
            r = self.command_ok('AT+HTTPACTION=1')
            if not r:
                self.command('AT+HTTPTERM\n')
                if not keep_session:
                    self.disconnect_gprs()
                return False
        if method == "GET":
            r = self.command_ok('AT+HTTPACTION=0')
            if not r:
                self.command('AT+HTTPTERM\n')
                if not keep_session:
                    self.disconnect_gprs()
                return False
        expire = time.monotonic() + http_timeout
        s = self.check_incoming()
        while s[0] != 'HTTPACTION_' + method and time.monotonic() < expire:
            time.sleep(0.1)
            s = self.check_incoming()
        if s[0] != 'HTTPACTION_' + method:
            logging.critical("SIM800L - Missing 'HTTPACTION' return message "
                "for '%s' method: %s", method, s)
            self.command('AT+HTTPTERM\n')
            if not keep_session:
                self.disconnect_gprs()
            return False
        valid = s[1]
        len_read = s[2]
        if len_read == 0:
            logging.debug("SIM800L - no data to be retrieved: %s", s)
        if not valid:
            logging.debug("SIM800L - invalid request: %s", s)
        if not valid or len_read == 0:
            self.command('AT+HTTPTERM\n')
            if not keep_session:
                self.disconnect_gprs()
            return False
        r = self.command('AT+HTTPREAD\n')
        params = r.split(':')
        if (len(params) == 2 and
                params[0] == '+HTTPREAD' and
                params[1].strip().isnumeric()):
            lr = int(params[1].strip())
            if len_read != lr:
                logging.critical(
                    "SIM800L - Different number of read characters: %d != %d",
                        len_read, lr)
                self.command('AT+HTTPTERM\n')
                if not keep_session:
                    self.disconnect_gprs()
                return False
        ret_data = ''
        expire = time.monotonic() + http_timeout
        while len(ret_data) < len_read and time.monotonic() < expire:
            ret_data += self.ser.read(len_read).decode(
                encoding='utf-8', errors='ignore')
        logging.debug(
            "Returned data: '%s'",
            ret_data.replace("\n", "\\n").replace("\r", "\\r"))
        r = self.check_incoming()
        if r != ("OK", None) and ret_data[-5:].strip() == 'OK':
            r = ("OK", None)
            ret_data = ret_data[:-6]
        if r != ("OK", None):
            logging.critical(
                "SIM800L - Missing 'OK' after reading characters: %s", r)
            self.command('AT+HTTPTERM\n')
            if not keep_session:
                self.disconnect_gprs()
            return False
        if len(ret_data) != len_read:
            logging.warning(
                "Length of returned data: %d. Expected: %d",
                len(ret_data), len_read)
        r = self.command_ok('AT+HTTPTERM')
        if not r:
            self.command('AT+HTTPTERM\n')
            if not keep_session:
                self.disconnect_gprs()
            return False
        if not keep_session:
            if not self.disconnect_gprs():
                self.command('AT+HTTPTERM\n')
                self.disconnect_gprs()
                return False
        return ret_data

    def read_and_delete_all(self, index_id=1):
        """
        Read the message at position 1, then delete all SMS messages, regardless
        the type (read, unread, sent, unsent, received)
        :return: text of the message
        """
        try:
            if index_id > 0:
                return self.read_sms(index_id)
        finally:
            self.command('AT+CMGDA="DEL ALL"\n', lines=1)
            self.check_incoming()

    def read_next_message(self, all_msg=False):
        """
        Check messages, read one message and then delete it.
        Can be repeatedly called to read messages one by one and delete them.
        :param all_msg: True if no filter is used (return both read and non read
            messages). Otherwise, only the non read messages are returned.
        :return: retrieved message text (string), otherwise: None = no messages
            to read; False = read error
        """
        if all_msg:
            rec = self.command('AT+CMGL="ALL",1\n')
        else:
            rec = self.command('AT+CMGL="REC UNREAD",1\n')
        if rec == "OK":
            return None
        if not rec:
            return False
        try:
            index_s = re.sub(r'\+CMGL: (\d*),"STO.*', r'\1', rec)
            if index_s.isnumeric():
                logging.critical("SIM800L - Deleting message: %s", rec)
                self.delete_sms(int(index_s))
                return False
        except Exception:
            return None
        try:
            index = int(re.sub(r'\+CMGL: (\d*),"REC.*', r'\1', rec))
            data = self.read_sms(index)
            self.delete_sms(index)
        except Exception:
            return False
        return data

    def command(self,
            cmdstr, lines=1, waitfor=500, msgtext=None, flush_input=True):
        """
        Executes an AT command
        :param cmdstr: AT command string
        :param lines: number of expexted lines
        :param waitfor: number of milliseconds to waith for the returned data
        :param msgtext: SMS text; to be used in case of SMS message command
        :param flush_input: True if residual input is flushed before sending
            the command. False disables flushing.
        :return: returned data (string); None in case of no data (or module error).
        """
        while self.ser.in_waiting and flush_input:
            flush = self.check_incoming()
            logging.debug("SIM800L - Flushing %s", flush)
        logging.log(5,  # VERBOSE
            "SIM800L - Writing '%s'",
            cmdstr.replace("\n", "\\n").replace("\r", "\\r"))
        self.ser.write(convert_gsm(cmdstr))
        if lines == 0:
            return None
        if msgtext:
            self.ser.write(convert_gsm(msgtext) + b'\x1A')
        if waitfor > 1000:  # this is kept from the original code...
            time.sleep((waitfor - 1000) / 1000)
        buf = self.ser.readline().strip()  # discard linefeed etc
        if lines == -1:
            if buf:
                buf = [buf] + self.ser.readlines()
            else:
                buf = self.ser.readlines()
            if not buf:
                return None
            result = ""
            for i in buf:
                result += convert_to_string(i) + "\n"
            return result
        if not buf:
            buf = self.ser.readline()
        if not buf:
            return None
        result = convert_to_string(buf)
        if lines > 1:
            self.savbuf = ''
            for i in range(lines - 1):
                buf = self.ser.readline()
                if not buf:
                    return result
                buf = convert_to_string(buf)
                if not buf == '' and not buf == 'OK' and not buf.startswith(
                        '+CMTI: "SM",'):
                    self.savbuf += buf + '\n'
        logging.log(5, "SIM800L - Returning '%s'", result)  # VERBOSE
        return result

    def command_ok(self,
                   cmd,
                   check_download=False,
                   check_error=False,
                   cmd_timeout=10):
        """
        Send AT command to the device and check that the return sting is OK
        :param cmd: AT command
        :param check_download: True if the "DOWNLOAD" return sting has to be
                                checked
        :param check_error: True if the "ERROR" return sting has to be checked
        :param cmd_timeout: timeout in seconds
        :return: True = OK received, False = OK not received. If check_error,
                    can return "ERROR"; if check_download, can return "DOWNLOAD"
        """
        logging.debug("SIM800L - Sending command '%s'", cmd)
        r = self.command(cmd + "\n")
        if not r:
            r = ""
        if r.strip() == "OK":
            return True
        if check_download and r.strip() == "DOWNLOAD":
            return "DOWNLOAD"
        if check_error and r.strip() == "ERROR":
            return "ERROR"
        if not r:
            expire = time.monotonic() + cmd_timeout
            s = self.check_incoming()
            while s[0] == 'GENERIC' and not s[1] and time.monotonic() < expire:
                time.sleep(0.1)
                s = self.check_incoming()
            if s == ("OK", None):
                return True
            if check_download and s == ("DOWNLOAD", None):
                return "DOWNLOAD"
            if check_error and s == ("ERROR", None):
                return "ERROR"
        logging.critical(
            "SIM800L - Missing 'OK' return message after: '%s': '%s'", cmd, r)
        return False

    def command_data_ok(self,
                   cmd,
                   check_download=False,
                   check_error=False,
                   cmd_timeout=10):
        """
        Send AT command to the device, read the answer and then check the
        existence of the OK message. "cmd" shall not have the ending newline.
        :param cmd: AT command
        :return: string in case of successful retrieval; otherwise None
            if module error or False if missing OK message
        """
        answer = self.command(cmd + '\n')
        if not answer:
            return None
        r = self.check_incoming()
        if r != ("OK", None):
            logging.error(
                "SIM800L - wrong '" + cmd + "' return message: %s", r)
            return False
        return answer

    def check_incoming(self):
        """
        Check incoming data from the module, decoding messages
        :return: tuple
        """
        buf = None
        if self.ser.in_waiting:
            buf = self.ser.readline()
            buf = convert_to_string(buf)
            while buf.strip() == "" and self.ser.in_waiting:
                buf = self.ser.readline()
                buf = convert_to_string(buf)
            if not buf:
                return "GENERIC", buf
            logging.debug("SIM800L - read line: '%s'", buf)
            params = buf.split(',')

            # +HTTPACTION (HTTP GET and PUT methods)
            if (len(params) == 3 and len(params[0]) == 14 and
                    params[0].startswith("+HTTPACTION: ")):
                valid = False
                try:
                    method = httpaction_method[params[0][-1]]
                except KeyError:
                    method = httpaction_method['X']
                try:
                    error_message = httpaction_status_codes[params[1]]
                except KeyError:
                    error_message = httpaction_status_codes['000']
                if params[1] in ('200', '301'):
                    valid = True
                else:
                    logging.critical(
                        'SIM800L - HTTPACTION_' + method +
                        ' return code: %s, %s="%s"',
                        buf, params[1], error_message)
                if params[1] == '301':
                    logging.info(
                        "SIM800L - HTTPACTION_GET 301 Moved Permanently.")
                if not params[2].strip().isnumeric():
                    return "HTTPACTION_" + method, False, 0
                return "HTTPACTION_" + method, valid, int(params[2])

            # +COPN (Read Operator Names)
            elif params[0].startswith("+COPN: "):
                numeric = params[0].split(':')[1].strip().replace('"', "")
                name = params[1].strip().replace('"', "").strip()
                return "COPN", numeric, name

            # +CFUN (Read Phone functionality indication)
            elif params[0].startswith("+CFUN: "):
                numeric = params[0].split(':')[1].strip()
                if numeric == "0":
                    logging.debug(
                        "SIM800L - CFUN - Minimum functionality.")
                if numeric == "1":
                    logging.debug(
                        "SIM800L - CFUN - Full functionality (Default).")
                if numeric == "4":
                    logging.debug(
                        "SIM800L - CFUN - Disable phone both transmit"
                        " and receive RF circuits.")
                return "CFUN", numeric

            # +CPIN (Read PIN)
            elif params[0].startswith("+CPIN: "):
                pin = params[0].split(':')[1].strip()
                return "PIN", pin

            # Call Ready
            elif params[0] == "Call Ready":
                return "MSG", params[0]

            # SMS Ready
            elif params[0] == "SMS Ready":
                return "MSG", params[0]

            # +CREG (Read Registration status)
            elif params[0].startswith("+CREG: "):
                numeric = params[0].split(':')[1].strip()
                if numeric == "0":
                    logging.debug(
                        "SIM800L - CREG - Not registered, not searching.")
                if numeric == "1":
                    logging.debug(
                        "SIM800L - CREG - Registered, home network.")
                if numeric == "2":
                    logging.debug(
                        "SIM800L - CREG - Not registered, searching.")
                if numeric == "3":
                    logging.debug(
                        "SIM800L - CREG - Registration denied.")
                if numeric == "4":
                    logging.debug(
                        "SIM800L - CREG - Unknown.")
                if numeric == "5":
                    logging.debug(
                        "SIM800L - CREG - Registered, roaming.")
                return "CREG", numeric

            # +CTZV (Read Time Zone)
            elif params[0].startswith("+CTZV: "):
                tz1 = params[0].split(':')[1].strip()
                tz2 = params[1].strip()
                return "CTZV", tz1, tz2

            # *PSUTTZ (Refresh time and time zone by network.)
            elif params[0].startswith("*PSUTTZ: "):
                year = params[0].split(':')[1].strip()
                month = params[1].strip()
                day = params[2].strip()
                hour = params[3].strip()
                minute = params[4].strip()
                second = params[5].strip()
                tz1 = params[6].strip().replace('"', "")
                tz2 = params[7].strip()
                return (
                    "PSUTTZ", year, month, day, hour, minute, second, tz1, tz2)

            # DST (Read Network Daylight Saving Time)
            elif params[0].startswith("DST: "):
                dst = params[0].split(':')[1].strip()
                return "DST", dst

            # RDY (Power procedure completed)
            elif params[0] == "RDY":
                return "RDY", None

            # +SAPBR (IP address)
            elif params[0].startswith("+SAPBR: "):
                ip_address = params[2].replace('"', "")
                if (params[0].split(':')[1].strip() == "1" and
                        params[1].strip() == "1"):
                    return "IP", ip_address
                return "IP", None

            # +CMTI (legacy code, partially revised) fires callback_msg()
            elif params[0].startswith("+CMTI"):
                self._msgid = int(params[1])
                if self.msg_action:
                    self.msg_action()
                return "CMTI", self._msgid

            # ERROR
            elif params[0] == "ERROR":
                return "ERROR", None

            # NO CARRIER (legacy code, partially revised) fires callback_no_carrier()
            elif params[0] == "NO CARRIER":
                self.no_carrier_action()
                return "NOCARRIER", None

            # +CDNSGIP (DNS query)
            elif params[0].startswith('+CDNSGIP: '):
                if params[0].split(':')[1].strip() != '1':
                    if params[1] == '8':
                        return "DNS", None, "DNS_COMMON_ERROR"
                    elif params[1] == '3':
                        return "DNS", None, "DNS_NETWORK_ERROR"
                    else:
                        return "DNS", None, "DNS_UNKNOWN_ERROR" + params[1]
                dns = params[2].replace('"', '').strip()
                logging.info("DNS: %s", dns)
                if len(params) > 3:
                    return "DNS", dns, params[3].replace('"', '').strip()
                else:
                    return "DNS", dns, params[1].replace('"', '').strip()

            # +CNTP (NTP sync)
            elif params[0].startswith('+CNTP: '):
                if params[0] == '+CNTP: 1':
                    logging.debug("SIM800L - Network time sync successful")
                    return "NTP", self.get_date(), 0
                elif params[0] == '+CNTP: 61':
                    logging.error("SIM800L - Sync time network error")
                    return "NTP", None, 61
                elif params[0] == '+CNTP: 62':
                    logging.error("SIM800L - Sync time DNS resolution error")
                    return "NTP", None, 62
                elif params[0] == '+CNTP: 63':
                    logging.error("SIM800L - Sync time connection error")
                    return "NTP", None, 63
                elif params[0] == '+CNTP: 64':
                    logging.error("SIM800L - Sync time service response error")
                    return "NTP", None, 64
                elif params[0] == '+CNTP: 65':
                    logging.error(
                        "SIM800L - Sync time service response timeout")
                    return "NTP", None, 65
                else:
                    logging.error(
                        "SIM800L - Sync time service - Unknown error code '%s'",
                        params[0])
                    return "NTP", None, 1

            # +CLIP (legacy code)
            elif params[0] == "RING" or params[0].startswith("+CLIP"):
                # @todo handle
                return "RING", None

            # OK
            elif buf.strip() == "OK":
                return "OK", None

            # DOWNLOAD
            elif buf.strip() == "DOWNLOAD":
                return "DOWNLOAD", None

        return "GENERIC", buf
