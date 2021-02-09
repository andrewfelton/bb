
import sys
sys.path.append('/Users/andrewfelton/Documents/bb/2021/python')
import selenium_utilities
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

driver = selenium_utilities.start_driver()

driver.get("https://fantasy.fangraphs.com/2021-starting-pitcher-ranks-january/")
time.sleep(2)
driver.current_url

soup = BeautifulSoup(driver.page_source, 'lxml')

table = soup.find(text="January SP List").parent.parent.find("table").find("tbody")
table_rows = table.find_all("tr")

l = []
for tr in table_rows:
    #print(tr)
    td = tr.find_all('td')
    row = [tr.text for tr in td]

    try:
        link = tr.find('a')
        fg_id = re.search("/([0-9]+)/stats", link['href']).group(1)
    except:
#        print(link)
        fg_id = ""
        fg_id = '15689' if (row[1]=='Luis Castillo') else fg_id
        fg_id = '14875' if (row[1]=='Caleb Smith') else fg_id
        fg_id = '11682' if (row[1]=='Carlos Martinez') else fg_id
        fg_id = '11423' if (row[1]=='Jose Quintana') else fg_id
        fg_id = '20302' if (row[1]=='David Peterson') else fg_id

    row.append(fg_id)
    l.append(row)

sporer_ranks = pd.DataFrame(l, columns=["Rank", "Name", "Team", "fg_id"])

