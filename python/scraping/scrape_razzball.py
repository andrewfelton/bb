import os
import time
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from datetime import date
from datetime import datetime
import re
from selenium.webdriver.common.action_chains import ActionChains
import sys
sys.path.append('python/general')
import selenium_utilities
sys.path.append('python/munging')
import player_names
import rosters


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

    # Copy the csv window into BS
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.find('table', id='neorazzstatstable')

    trows = table.findAll('tr')
    streamers = []
    for trow in trows:
        streamer = []
        tds = trow.findAll('td')
        if [] == list(set(trow['class']) & set(['class=sorter-head', 'tablesorter-headerRow', 'tablesorter-ignoreRow'])):
            player_url = tds[1].find('a')['href']
            player_id = player_url.split('/')[4]
            streamer.append(player_id) # Razz ID
            player_name = tds[1].find('a').text
            streamer.append(player_name) # player name
            opponent =tds[3].text
            streamer.append(opponent) # Opponent
            date_str =tds[4].text + '/2021'
            streamdate = datetime.strptime(date_str, '%m/%d/%Y')
            streamer.append(streamdate) # Date
            streamer.append(float(tds[8].text)) # value
            streamer.append(float(tds[9].text)) # QS
            streamer.append(float(tds[12].text)) # IP
            streamer.append(float(tds[15].text)) # SO
            streamer.append(float(tds[21].text)) # ERA
            streamer.append(float(tds[22].text)) # ERA
            streamers.append(streamer)


    df_streamers = pd.DataFrame(streamers, columns=['razz_id', 'name', 'opponent', 'date', 'value', 'qs', 'ip', 'so', 'era', 'whip'])
    names = player_names.get_player_names()
    df_streamers = df_streamers.merge(right=names[['mlb_id', 'fg_id']], how='left', left_on='razz_id', right_on='mlb_id')
    df_streamers['fg_id'] = df_streamers.apply(lambda row: row['fg_id'] if str(row['fg_id'])!='nan' else row['razz_id'], axis=1)

    ff_rosters = rosters.get_ff_ownership()
    df_streamers = df_streamers.merge(right=ff_rosters[['Team', 'Player', 'fg_id']], how='left', on='fg_id')

    # Save on computer as .csv file
    mysystem = 'razz'
    today = date.today().strftime("%Y%m%d")
    basename = "/Users/andrewfelton/Documents/bb/2021/data/" + mysystem + '/' + mysystem + "_" + mytype
    new_file = basename + "_" + today + ".csv"
    df_streamers.to_csv(new_file)

    # create the soft link
    ln_file = basename + ".csv"
    command_ln = os.popen('ln -sf ' + new_file + ' ' + ln_file)
    print(command_ln)

    # print the best streamers
    best_streamers = df_streamers[df_streamers['Team'].isna()].sort_values(by='qs', ascending=False)
    best_streamers = best_streamers[['fg_id', 'name', 'opponent', 'date', 'value', 'qs', 'era']]
    print('Five best upcoming prob of QS:')
    print(best_streamers.head(5))

    # Close it down
    driver.close()
    selenium_utilities.stop_selenium('bbsel')



#scrape_razz(mytype='pitchers', url="https://razzball.com/steamer-pitcher-projections/")
#time.sleep(2)
#scrape_razz(mytype='batters', url="https://razzball.com/steamer-hitter-projections/")

#scrape_razz(mytype='streamers', url="https://razzball.com/streamers/")
