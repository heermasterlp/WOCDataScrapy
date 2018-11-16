from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import sys
import requests
import re
import math


options = Options()
options.headless = True
driver = webdriver.Firefox(options=options, executable_path='geckodriver.exe')

root = 'http://www.webofknowledge.com/'
s = requests.get(root)
sid = re.findall(r'SID=\w+&', s.url)[0].replace('SID=', '').replace('&', '')
print('sid:', sid)

first_page = 'https://apps.webofknowledge.com/WOS_AdvancedSearch_input.do?product=WOS&search_mode=AdvancedSearch&SID=' + sid.strip()
driver.get(first_page)
time.sleep(3)



driver.quit()