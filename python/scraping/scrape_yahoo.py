import sys
sys.path.append('python/utilities')
import selenium_utilities
import postgres
from bs4 import BeautifulSoup
import pandas as pd
sys.path.append('python/munging')
import player_names
import gspread
import gspread_dataframe as gsdf


driver = selenium_utilities.start_driver()

league_url = 'https://baseball.fantasysports.yahoo.com/b1/26574/'
driver.get(league_url + 'startingrosters')
print(driver.current_url)

bs_rosters = BeautifulSoup(driver.page_source, 'lxml')
main_div = bs_rosters.find('div', id='yspmaincontent')
tables = main_div.find_all('div', {'class':'Grid-u-1-2 Pend-xl'})

rosters = []
for table in tables:
    #roster = []
    owner = table.find('p').text
    player_rows = table.find('table').find_all('tr')
    for player_row in player_rows:
        player = player_row.find('div').find('div')
        if (player!=None):
            player = player.find('a')
            playerid = str(player['href'].split('/')[-1])
            playername = player.text
            rosters.append([owner, playerid, playername])

rosters = pd.DataFrame(rosters, columns=['Owner', 'yahoo_id', 'name'])

names = player_names.get_player_names()
rosters = pd.merge(
    rosters[['Owner', 'yahoo_id']],
    names[['yahoo_id', 'fg_id']],
    on='yahoo_id',
    how='left'
)


gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
sh = gc.open("BB 2021")
gc_yahoo_rosters = sh.worksheet('Legacy SoS Rosters')
gsdf.set_with_dataframe(gc_yahoo_rosters, rosters)


if (1==0):
    yahoo_names = rosters['Team','yahoo_id','name']
    yahoo_names['name_strip'] = yahoo_names['name'].str.lower().str.replace('.','').str.replace('ó','o').str.replace('á','a').str.replace('ñ','n').str.replace('í','i').str.replace('é','e').str.replace('ú','u')
    names['name_strip'] = names['Canonical'].str.lower().str.replace('.', '').str.replace('ó','o').str.replace('á','a').str.replace('ñ','n').str.replace('í','i').str.replace('é','e').str.replace('ú','u')

    name_matches = pd.merge(
        yahoo_names[['name_strip', 'yahoo_id']],
        names[['name_strip', 'Canonical']],
        on='name_strip',
        how='left'
    )
    name_matches.to_csv('~/Documents/bb/2021/yahoo_names.csv')
