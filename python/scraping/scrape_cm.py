def scrape_cm_draft(draft_num, gs=None, db=None):

    import sys
    sys.path.append('python/utilities')
    import selenium_utilities
    import postgres
    sys.path.append('python/munging')
    import player_names
    import time
    from bs4 import BeautifulSoup
    import pandas as pd
    import gspread
    import gspread_dataframe
    import re

    driver = selenium_utilities.start_driver()

    #draft_num = '46233' # Testing
    #draft_num = '46117' # SoS Mock
    #draft_num = '46233' # SoS D2
    #draft_num = '46234' # SoS D2
    draft_url = "https://www.couchmanagers.com/mock_drafts/draft_chart.php?draftnum="+str(draft_num)
    draft_url = "https://www.couchmanagers.com/mock_drafts/csv/download.php?draftnum="+str(draft_num)

    driver.get(draft_url)
    time.sleep(2)
    print('Arrived at '+driver.current_url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    selenium_utilities.stop_selenium('bbsel')

    #csv_path = "/Users/andrewfelton/Downloads/docker/FanGraphs\ Leaderboard.csv"


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
        row = [td.get_text(separator=' ').strip() for td in tds[1:]]
        row = [re.sub('\s+', ' ', td) for td in row]
        print('Round ' + str(round) + ': ' + str(row))
        if (teamnames!=row):
            mockdraft.append(row)

    mock = pd.DataFrame(mockdraft, columns=teamnames)

    teams = pd.DataFrame(mock.columns, columns=['Team'])
    teams['Order'] = teams.reset_index().index + 1


    #mock.to_csv('./data/couchmanagers/mockdraft_'+draft_num+'.csv')
    mock_long = mock.unstack().reset_index()
    #mock_long.to_csv('./data/couchmanagers/mockdraft_'+draft_num+'.csv')
    mock_long.columns = ['Team', 'Round', 'Player']

    mock_long = mock_long.merge(
        teams,
        how='outer',
        on='Team'
    )

    mock_long['Pick'] = (len(teams) * mock_long['Round']) + mock_long['Order']
    mock_long = mock_long.sort_values(by='Pick')
    mock_long['Round'] = mock_long['Round']+1


    names = player_names.get_player_names()





    if (gs!=None):
        gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
        bb2021 = gc.open("BB 2021")
        sheettitle = "Mock "+draft_num
        bb2021.values_clear(sheettitle + "!A:Z")
        gspread_dataframe.set_with_dataframe(bb2021.worksheet(sheettitle), mock_long)
        combined = bb2021.worksheet('Combined')
        hitter_projections = bb2021.worksheet('Hitter Projections')
        combined.update
        hitter_projections.update

    if (db!=None):
        bbdb = postgres.connect_to_bbdb()
        mock_long.to_sql('cm_mock_'+draft_num, bbdb, schema='drafts', if_exists='replace')




#scrape_cm_draft(draft_num='46233', db=True)



import urllib3

http = urllib3.PoolManager()

filepath = '~/Downloads/cm_draft_'+draft_num+'.csv'

import requests
import csv
r = requests.get(draft_url).text.splitlines()


mock = []
for line in r:
    pick = line.split(',')
    for i in range(0, len(pick)):
        pick[i] = pick[i].replace('"','')
    mock.append(pick)
mock = pd.DataFrame(mock)
