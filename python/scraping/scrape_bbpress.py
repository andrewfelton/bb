import sys
from typing import Text
sys.path.append('python/general')
import selenium_utilities
import postgres
from bs4 import BeautifulSoup
import pandas as pd
sys.path.append('python/munging')
import requests





url = 'https://www.baseballpress.com/lineups'
print('Scraping from '+url)
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')
tables = soup.find_all('div', {'class':'col-md-6 col-xl-4 lineup-col'})

df_lineups = pd.DataFrame()
lineups = []
for table in tables:
    header_div = table.find('div', {'class':'lineup-card-header'})
    team_links = header_div.find_all('a', {'class':'mlb-team-logo bc'})
    datetimebox = header_div.find_all('div', {'class':'col col--min c'})[1]
    date = datetimebox.find_all('div')[0].text.strip()
    time = datetimebox.find_all('div')[1].text.strip()

    lineups_div = table.find('div', {'class':'lineup-card-body'}).find_all('div', {'class':'col col--min'})
    team_no = 0
    for lineup_div in lineups_div:
        if lineup_div.text.strip() != 'No Lineup Released':
            lineup = []
            df_lineup = pd.DataFrame()
            team = team_links[1].text.strip()
            team_no = team_no+1
            position = 0
            for spot in lineup_div.find_all('div', {'class':'player'}):
                player = {}
                player['team'] = team
                player['date'] = date
                player['time'] = time
                position = position+1
                player['position'] = position
                player['name'] = spot.find('a').text
                player['mlb_id'] = spot.find('a')['data-mlb']
                player['razz_url'] = spot.find('a')['data-razz']
                if player['razz_url']!='':
                    player['razz_id'] = player['razz_url'].split('/')[4]
                player['bbref_id'] = spot.find('a')['data-bref']
                #print(player)
                lineup.append(player)
                df_lineup.append(pd.DataFrame(player, index=[0]))
            lineups.append(lineup)
            df_lineups.append(df_lineup)






if 1==2:
    for lineup in lineups:
        for spot in lineup:
            print(spot)

