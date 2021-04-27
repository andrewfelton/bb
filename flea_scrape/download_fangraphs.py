from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import glob
import os
import time
import zipfile
import datetime



fldr_dwnld = '/Users/andrewfelton/Downloads'


chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option("prefs", {
  "download.default_directory": fldr_dwnld,
  "download.prompt_for_download": False,
})





def dwnld_file(playertype, projsystem, zf):
  fldr_dwnld = '/Users/andrewfelton/Downloads'
  driver.get("https://www.fangraphs.com/projections.aspx?pos=all&stats="+playertype+"&type="+projsystem)
  driver.find_element_by_id("ProjectionBoard1_cmdCSV").click()
  time.sleep(10)
  suffix = "batters" if (playertype == "bat") else "pitchers"
  filename = projsystem + "_" + suffix + ".csv"
  os.chdir(fldr_dwnld)
  os.rename('FanGraphs Leaderboard.csv', filename)
  zf.write(filename)
  os.remove(filename)




today = datetime.date.today()
str_today = str(today)
os.chdir('/Users/andrewfelton/Downloads')
zf = zipfile.ZipFile('projections_'+str_today+'.zip', mode='w')


driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.fangraphs.com')
time.sleep(10)
btn_no_thanks = driver.find_element_by_class_name("my_popup_close")
if (btn_no_thanks):
  btn_no_thanks.click()


dwnld_file('bat', 'thebat', zf)
dwnld_file('pit', 'thebat', zf)
dwnld_file('bat', 'fangraphsdc', zf)
dwnld_file('pit', 'fangraphsdc', zf)
driver.close()
zf.close()
