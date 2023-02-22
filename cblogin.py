#imports
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# https://stackoverflow.com/questions/64165726/selenium-stuck-on-checking-your-browser-before-accessing-url
# install virtual display for headless website browsing
from pyvirtualdisplay.display import Display
display = Display(visible=0, size=(1920, 2160))
display.start()
# https://stackoverflow.com/questions/67341346/how-to-bypass-cloudflare-bot-protection-in-selenium
# options for driver (browser)
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('enable-automation')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-browser-side-navigation')
#chrome_options.add_argument("--remote-debugging-port=9222")
#chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-gpu')
#chrome_options.add_argument("--log-level=3")
#driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',options=chrome_options)

# https://stackoverflow.com/questions/74188360/selenium-cloudflare-colab-and-json
from seleniumbase import Driver
from seleniumbase import page_actions

driver = Driver(uc=True)

time.sleep(random.randint(2,4))

login_url = "https://chaturbate.eu/auth/login/"
following_url = "https://chaturbate.eu/followed-cams/"

pattern = re.compile('<a data-room=".*>(.*)<\/a>')

login = 'bernie_78'
#login = input("Chaturbate login: ")
passw = 'Chaturbate_ifjmu9a!'
#passw = input("Chaturbate password: ")

print('open CB login-page')
driver.get(login_url)
#time.sledep(random.randint(4,10))
r = driver.page_source
#time.sleep(random.randint(4,10))
soup = BeautifulSoup(r, 'html.parser')


with open('cblogin.html','w', encoding='utf-8') as t:
    os.chmod('cblogin.html', 0o666)
    t.write(str(soup))

print('sending login data')
# input and password field
username = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/form/fieldset/table/tbody/tr[1]/td/input')
password = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/form/fieldset/table/tbody/tr[4]/td/input')
username.send_keys(login)
password.send_keys(passw)
# checkbox 'remember me'
driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/form/fieldset/table/tbody/tr[6]/td/input').click()
driver.save_screenshot("cblogin.png")
# login button
#WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/div/div/form/input[3]'))).click()
driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/form/input[3]').click()


driver.switch_to.default_content()
driver.save_screenshot("cbafterclick.png")
# confirm user agreement if pops up
print('navigating to followed-cams')
try: 
    driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/div[3]/a[2]').click()
except: pass
driver.save_screenshot("cbsuccess.png")

# open online following page
driver.get(following_url)
#driver.save_screenshot("cbfollowedonline.png")
#r = driver.page_source
#soup = BeautifulSoup(r, 'html.parser')
#soup = str(soup)

#for match in pattern.finditer(soup):
    #broadcaster = match.group(1).strip()
    #print(broadcaster)
    #with open('cbfollowedonline.txt','a', encoding='utf-8') as t:
        #os.chmod('cbfollowedonline.txt', 0o666)
        #t.write(str(broadcaster)+'\n')

# open offline following page
#driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div[2]/div[3]/div[2]/div[1]/div[2]/p/a').click()
#driver.save_screenshot("cbfollowedoffline.png")


status = 'online'

for page in range(1,10):
    print(status  + ' page: ' + str(page))
    time.sleep(random.randint(2,4))
    driver.save_screenshot("cbfollowedoonline_"+str(page)+'_'+status+".png")
    # open online following page
    r = driver.page_source
    soup = BeautifulSoup(r, 'html.parser')
    soup = str(soup)

    for match in pattern.finditer(soup):
        broadcaster = match.group(1).strip()
        with open('cbfollowedonline.txt','a', encoding='utf-8') as t:
            os.chmod('cbfollowedonline.txt', 0o666)
            t.write(str(broadcaster)+'\n')
    try:
        driver.find_element(By.CLASS_NAME, 'next').click()
    except Exception as e:
        #print(e)
        status = 'offline'
        break

#open offline following page        
driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div[2]/div[3]/div[2]/div[1]/div[2]/p/a').click()

for page in range(1,25):
    print(status  + ' page: ' + str(page))
    time.sleep(random.randint(2,4))
    driver.save_screenshot("cbfollowedoonline_"+str(page)+'_'+status+".png")
    # open online following page
    r = driver.page_source
    soup = BeautifulSoup(r, 'html.parser')
    soup = str(soup)

    for match in pattern.finditer(soup):
        broadcaster = match.group(1).strip()
        with open('cbfollowedonline.txt','a', encoding='utf-8') as t:
            os.chmod('cbfollowedonline.txt', 0o666)
            t.write(str(broadcaster)+'\n')
    try:
        driver.find_element(By.CLASS_NAME, 'next').click()
    except Exception as e:
        #print(e)
        break
        
driver.close()
driver.quit()