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
gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')

#draft_num = '46108' # Testing
draft_num = '46117' # SoS Mock
draft_url = "https://www.couchmanagers.com/mock_drafts/draft_chart.php?draftnum="+draft_num
driver.get(draft_url)
time.sleep(2)
print('Arrived at '+driver.current_url)

soup = BeautifulSoup(driver.page_source, 'lxml')
table = soup.find('table', 'all_teams_table')

table_rows = table.find_all('tr')


teamnames = []
tds = table_rows[0].find_all('td')
for td in tds[1:]:
    teamnames.append(td.text.strip())


mockdraft = []
round = 0
for tr in table_rows[1:]:
    round += 1
    tds = tr.find_all('td')
    row = [td.get_text(separator=' ') for td in tds[1:]]
    print('Round 3: ' + str(row))
    mockdraft.append(row)

mock = pd.DataFrame(mockdraft, columns=teamnames)

teams = pd.DataFrame(mock.columns, columns=['Team'])
teams['Order'] = teams.reset_index().index


#mock.to_csv('./data/couchmanagers/mockdraft_'+draft_num+'.csv')

mock_long = mock.unstack().reset_index()
#mock_long.to_csv('./data/couchmanagers/mockdraft_'+draft_num+'.csv')
mock_long.columns = ['Team', 'Round', 'Player']


mock_long = mock_long.merge(
    teams,
    how='outer',
    on='Team'
)

mock_long['Pick'] = len(teams) * mock_long['Round'] + mock_long['Order'] + 1
mock_long = mock_long.sort_values(by='Pick')
mock_long['Round'] = mock_long['Round']+1


bb2021 = gc.open("BB 2021")
sheettitle = "Mock "+draft_num

bb2021.values_clear(sheettitle + "!A:Z")
gspread_dataframe.set_with_dataframe(bb2021.worksheet(sheettitle), mock_long)


combined = bb2021.worksheet('Combined')
hitter_projections = bb2021.worksheet('Hitter Projections')

combined.update

selenium_utilities.stop_selenium('bbsel')
