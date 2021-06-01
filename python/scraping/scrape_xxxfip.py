import os
from datetime import date
from datetime import datetime
import time
from bs4 import BeautifulSoup
import pandas as pd
import sys
sys.path.append('python/general')
import selenium_utilities
sys.path.append('python/munging')
import player_names
import rosters
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import postgres

def scrape_xxxfip():
    import glob
    import csv
    bbdb = postgres.connect_to_bbdb()

    # Get the home page
    driver = selenium_utilities.start_driver(headless=True)
    driver.get("https://mlpitchquality.shinyapps.io/xxxfip_app/")
    time.sleep(5)
    input_submit = driver.find_element_by_id('download_but')
    input_submit.click()
    time.sleep(5)
    driver.close()
    print('Closed driver, hopefully successfully scraped xxxfip data')

    dl_location = "/Users/andrewfelton/Downloads/docker/*.*"
    dl_file = max(glob.glob(dl_location), key=os.path.getmtime)
    filename = dl_file.split('/')[-1]
    asof_date = filename.split('_')[2].split('.')[0]
    assert(filename.split('_')[0] == 'xxxFIP')
    print('Downloaded file ' + dl_file)

    basepath = "/Users/andrewfelton/Documents/bb/bb-2021/data/xxxfip/"
    new_file = basepath + filename
    stream_command = os.popen('mv ' + dl_file + ' ' + new_file)
    mv_file = stream_command.read()

    # create the soft link
    ln_file = basepath + "xxxfip.csv"
    command_ln = os.popen('ln -sf ' + new_file + ' ' + ln_file)

    xxxfip = pd.read_csv(ln_file)
    xxxfip.insert(0, 'asof_date', asof_date)
    
    # Merge in the FG IDs
    # We only have name to match on so need to do some manual adjustments
    xxxfip.rename(columns={
        'Name':'name',
        'Batters Faced':'batters_faced'
        }, inplace=True)
    names = player_names.get_player_names()
    xxxfip = xxxfip.merge(right=names[['name', 'fg_id']], how='left', on='name')
    xxxfip.loc[(xxxfip['name'] == 'JT Brubaker'),'fg_id']='17578'
    xxxfip.loc[(xxxfip['name'] == 'Hyun Jin Ryu'),'fg_id']='14444'
    xxxfip.loc[(xxxfip['name'] == 'Kwang Hyun Kim'),'fg_id']='27458'

    
    #fg_ids = xxxfip[['playerid']].astype(str).values
    #put_missing_in_GS(id_list=pd.DataFrame(fg_ids, columns=['fg_id']), type='fg_id')

    xxxfip = xxxfip[[
        'asof_date', 'fg_id', 'xxxFIP'
    ]]
    schema = 'tracking'
    tablename = 'xxxfip'
    bbdb = postgres.connect_to_bbdb()
    xxxfip.to_sql(tablename, bbdb, schema=schema, if_exists='replace')

    return xxxfip


