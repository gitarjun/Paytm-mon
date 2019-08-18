from win10toast import ToastNotifier
from lxml import etree
import re
import time
import winreg
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import winsound
import traceback
import os
import datetime
REG_PATH = r"Environment"
current_path = os.path.dirname(os.path.realpath(__file__))

def time_now():
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

from conwriter import conprint

class ShipentMon:
    def __init__(self,shipment_id):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0")
        service_args = ['--load-images=yes', '--disk-cache=yes', '--max-disk-cache-size=102400', ]
        self.driver = webdriver.PhantomJS(service_args=service_args, desired_capabilities=dcap)
        self.crazzy_frog = [('659', '460'), ('784', '340'), ('659', '230'),
                       ('659', '110'), ('880', '230'), ('659', '230'),
                       ('587', '230'), ('659', '460'), ('988', '340'),
                       ('659', '230'), ('659', '110'), ('1047', '230'),
                       ('988', '230'), ('784', '230'), ('659', '230'),
                       ('988', '230'), ('1318', '230'), ('659', '110'),
                       ('587', '230'), ('587', '110'), ('494', '230'),
                       ('740', '230'), ('659', '460')]
        self.loc_string = None
        self.shipment_id = str(shipment_id)

    def set_reg(self,name, value):
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                          winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False

    def get_reg(self,name):
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                          winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, name)
            winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return None

    def web_driver_wait(self, xpath, time=15):
        try:
            return WebDriverWait(self.driver, time).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except:
            return 0

    def make_toast(self,cur_location,date_time,other):
        toaster = ToastNotifier()
        loc = "Shipment @ {}".format(cur_location)
        stat = " - ".join(date_time + other)
        toaster.show_toast(loc, stat, icon_path="python.ico" ,duration=5, threaded=True)
        while toaster.notification_active():
            for f, l in self.crazzy_frog:
                winsound.Beep(int(f), int(l))

    def run_mon(self):
        try:
            self.driver.get("http://www.xpressbees.com/track-shipment.aspx")
        except:
            return 0

        txt_field = self.web_driver_wait('//*[@id="ContentPlaceHolder1_txtShippingIds"]')
        button = self.web_driver_wait('//*[@id="ContentPlaceHolder1_btnTrackShipment"]')
        txt_field.clear()
        txt_field.send_keys(self.shipment_id)
        button.click()

        cur_location = self.web_driver_wait('//*[@id="ContentPlaceHolder1_gvTrackShipment"]/tbody/tr[2]/td[5]').text
        table = self.web_driver_wait('//*[@id="ContentPlaceHolder1_gvTrackShipment_gvViewShipmentDetails_0"]/tbody')

        html = table.get_attribute('innerHTML')
        x = etree.HTML(html)
        rows = x.getchildren()[0].getchildren()

        dta = etree.tostring(rows[1], pretty_print=True)
        date_time = re.findall(r'0">(.*?)</', dta.decode())
        other = re.findall(r'px;">(.*?)</td', dta.decode())

        if self.get_reg('ShipmentStatus') is None:
            self.set_reg("ShipmentStatus", str(len(rows)))
        elif len(rows)>int(self.get_reg('ShipmentStatus')):
            self.set_reg("ShipmentStatus", str(len(rows)))
            self.make_toast(cur_location,date_time,other)

        self.driver.get_screenshot_as_file('Status.png')
        self.loc_string = " | ".join(other[1:])

    def ret_status(self):
        try:
            self.run_mon()
        except Exception as E:
            with open(current_path + '\\Error_Log.txt', 'a') as fil:
                fil.write('\n{0} {1} {0}\n'.format("#" * 10, time_now()))
                fil.write(traceback.format_exc())
                fil.write('\n#################################\n')
        finally:
            self.driver.quit()

if __name__=="__main__":
    con_print = conprint(space=100,speed=3)
    print("[+]Mointering started @ {}\n".format(time_now()))
    while True:
        proc = ShipentMon() # Shipment ID goes here
        try:
            con_print.reset_curser()
            con_print.con_write("Checking Now")
            proc.ret_status()
            str2write = proc.loc_string
            if str2write is None:
                con_print.reset_curser()
                con_print.con_write("No Connection to Server")
                time.sleep(15)
                continue
            con_print.reset_curser()
            for i in range(900,0,-1):
                time.sleep(1)
                con_print.con_write("{} ({})".format(proc.loc_string,i))

        except KeyboardInterrupt:
            con_print.terminate()
            print("\n\n[+]Mointering stopped @{}".format(time_now()))
            break

