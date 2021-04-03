import os
import time
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from datetime import date
from selenium.webdriver.common.action_chains import ActionChains
import sys
sys.path.append('python/general')
import selenium_utilities

def scrape_razz(mytype, url):
    driver = selenium_utilities.start_driver()

    # Log in
    driver.get("https://razzball.com/wp-login.php?redirect_to=https%3A%2F%2Frazzball.com")
    time.sleep(2)
    input_login = driver.find_element_by_id('user_login')
    input_login.send_keys('andy.felton+razz@gmail.com')
    input_pw = driver.find_element_by_id('user_pass')
    input_pw.send_keys('36Pm4jKml7')
    input_submit = driver.find_element_by_id('wp-submit')
    input_submit.click()
    time.sleep(2)

    # Go to the projections page
    driver.get(url)
    time.sleep(5)
    print("Arrived at "+url)

    # Click to download
    # Use the "popup" as csv b/c trouble with the download button
    action = ActionChains(driver)
    btn_dl = driver.find_element_by_xpath('//div/div[2]/div/table[1]/tbody/tr[1]/td[4]/button')
    action.move_to_element(btn_dl).click().perform()
    time.sleep(1)
    driver.switch_to_window(driver.window_handles[1])

    # Copy the csv window into BS
    soup = BeautifulSoup(driver.page_source, 'lxml')
    raw_csv = StringIO(soup.find('body').text)
    table = pd.read_csv(raw_csv)

    # Save on computer as .csv file
    mysystem = 'razz'
    today = date.today().strftime("%Y%m%d")
    basename = "/Users/andrewfelton/Documents/bb/2021/data/" + mysystem + '/' + mysystem + "_" + mytype
    new_file = basename + "_" + today + ".csv"
    table.to_csv(new_file)

    # create the soft link
    ln_file = basename + ".csv"
    command_ln = os.popen('ln -sf ' + new_file + ' ' + ln_file)
    print(command_ln)

    # Close it down
    driver.close()
    selenium_utilities.stop_selenium('bbsel')



#scrape_razz(mytype='pitchers', url="https://razzball.com/steamer-pitcher-projections/")
#time.sleep(2)
#scrape_razz(mytype='batters', url="https://razzball.com/steamer-hitter-projections/")

#scrape_razz(mytype='streamers', url="https://razzball.com/streamers/")
