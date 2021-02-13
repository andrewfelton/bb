import sys
sys.path.append('/Users/andrewfelton/Documents/bb/2021/python')
import selenium_utilities
from selenium import webdriver
from bs4 import BeautifulSoup

driver = selenium_utilities.start_driver()

league_url = 'https://baseball.fantasysports.yahoo.com/b1/26574/'
driver.get(league_url + 'startingrosters')


print(driver.current_url)

bs_rosters = BeautifulSoup(driver.page_source, 'lxml')

main_div = bs_rosters.find('div', id='yspmaincontent')
tables = main_div.find_all('div')

#print(tables[1])

owner = tables[0].find('p')

print(owner)