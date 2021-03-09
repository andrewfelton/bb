import sys
sys.path.append('python/utilities')
import selenium_utilities
import postgres
from bs4 import BeautifulSoup
import pandas as pd
sys.path.append('python/munging')
import import_names
import gspread
import gspread_dataframe as gsdf


driver = selenium_utilities.start_driver()

url = 'https://www.baseballpress.com/lineups'
driver.get(url)
print('Arrived at ' + str(driver.current_url))

soup = BeautifulSoup(driver.page_source, 'lxml')
tables = soup.find_all('div', {'class':'col-md-6 col-xl-4 lineup-col'})



