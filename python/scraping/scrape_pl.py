import sys
sys.path.append('/Users/andrewfelton/Documents/bb/2021/python')
import selenium_utilities
import time
from bs4 import BeautifulSoup
import pandas as pd
import gspread
#from df2gspread import df2gspread as d2g
import gspread_dataframe

driver = selenium_utilities.start_driver()
draft_url = "https://www.pitcherlist.com/way-too-early-top-100-starting-pitcher-rankings-for-2021/"
driver.get(draft_url)
time.sleep(2)
print('Arrived at '+driver.current_url)

soup = BeautifulSoup(driver.page_source, 'lxml')
table = soup.find('table', class_="list")

t = pd.read_html(str(table))[0]
t.to_csv('pl.csv')
