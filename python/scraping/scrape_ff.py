def login():
    import time

    driver = selenium_utilities.start_driver()
    driver.get("https://www.fleaflicker.com/mlb/login")
    time.sleep(2)
    driver.current_url

    input_login = driver.find_element_by_name('email')
    input_login.send_keys('andy.felton@gmail.com')
    input_pw = driver.find_element_by_name('password')
    input_pw.send_keys('9X7@eCmF$ZMb')
    input_submit = driver.find_element_by_xpath('//*[@id="body-center-main"]/form/div/div[2]/button')
    input_submit.click()
    time.sleep(2)

    return driver


def rosters(league, upload_to_db=True):
    import sys
    import datetime
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    from general import classes
    from munging import player_names
    from general import postgres


    print('\n--------------------------\nScraping Fleaflicker rosters for league:'+league.league_name+'\n')
    assert(league.league_platform == 'fleaflicker')
    league_num = league.league_num

    roster_url = 'https://www.fleaflicker.com/mlb/leagues/'+league_num+'/teams'
    page = requests.get(roster_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    main_div = soup.find('div', id='body-center-main')
    tables = main_div.find_all('table')

    today = datetime.date.today()
    str_today = str(today)

    teams = []

    for t in tables:
        trows = t.find_all('tr')
        for tr in trows:
            if (tr.find("span", {"class": "league-name"})): # Found the span with the team name
                team_name = tr.find("span", {"class": "league-name"}).text
                #print('New team: '+team_name)
                teams.append(classes.FantasyTeam(team_name))
                current_team = teams[-1]
            elif tr.find('a', {"class": "player-text"}):
                player_data = tr.find('a', {"class": "player-text"})
                player_name = player_data.text
                player_url = 'https://www.fleaflicker.com' + player_data['href']
                player_ff_id = player_data['href'].split('/')[-1].split('-')[-1]
                current_team.add_player(player_name, player_ff_id)

    df_export = pd.DataFrame(columns=['Team','Player','ff_id'])
    for team in teams:
        df_export = pd.concat([df_export, team.to_dataframe()])
    df_export.reset_index(drop=True, inplace=True)

    names = player_names.get_player_names()
    df_export = df_export.merge(right=names[['ff_id', 'fg_id']], how='left', on='ff_id')

    # Go through the Fleaflicker players that don't have matching FG IDs
    missing_fg_id = df_export[df_export['fg_id'].isna()]
    if len(missing_fg_id)>0:
        print('Miising fg_id for '+str(len(missing_fg_id.values))+' player(s):')
        for player in missing_fg_id.values.tolist():
            print('\nMissing info on:')
            print(player)
            ff_match = player_names.find_other_ids_w_ff(player[2])


    file_rosters = '/Users/andrewfelton/Documents/bb/bb-2021/data/rosters/rosters_'+league_num+'_'+str_today+'.csv'
    df_export.to_csv(file_rosters, index=False)
    print('Saved rosters to ' + file_rosters)

    if upload_to_db:
        bbdb = postgres.connect_to_bbdb()
        df_export.to_sql('sos', con=bbdb, schema='rosters', if_exists='replace', index=False)
        print('Uploaded to database')

        player_names.push_player_names_to_gs()
        print('Updated Google Sheets')

    return df_export


def team_rosters():
    import datetime
    from bs4 import BeautifulSoup
    import pandas as pd

    assert(league.league_platform == 'fleaflicker')
    league_num = league.league_num


    roster_url = 'https://www.fleaflicker.com/mlb/leagues/'+league_num
    page = requests.get(roster_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    league_names_divs = soup.find_all('div', {'class':'league-name'})
    for league_names_div in league_names_divs:
        #print(league_names_div)

        team_roster_url = 'https://www.fleaflicker.com' + league_name_div.find('a')['href']
        league_num = team_roster_url.split('/')[-1]
        team_roster_page = requests.get(team_roster_url)
        team_roster_soup = BeautifulSoup(page.text, 'html.parser')
        main_table = team_roster_soup.find('div', {'id': 'body-center-main'}).find('table')
        trows = main_table.find_all['tr']



def scrape_standings(league):
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    import datetime
    from general import postgres

    assert(league.league_platform == 'fleaflicker')
    league_num = league.league_num

    roster_url = 'https://www.fleaflicker.com/mlb/leagues/'+league_num
    page = requests.get(roster_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    main_div = soup.find('div', id='body-center-main')
    tables = main_div.find('table')
    trows = tables.find_all('tr')
    standings = []
    for trow in trows[2:]:
        standing = []
        tds = trow.find_all('td')
        standing.append(tds[0].text)
        for i in range(3,15):
            standing.append(tds[i].find('span').text)
        standings.append(standing)
    df_standings = pd.DataFrame(standings, columns=['team','hr','r','rbi','sb','obp','ops','so','sv','hld','era','whip','qs'])

    today = datetime.date.today()
    df_standings['date'] = today
    str_today = str(today)

    bbdb = postgres.connect_to_bbdb()
    df_standings.to_sql(name='standings_sos', con=bbdb, schema='tracking', index=False, if_exists='replace')


# scrape_standings(league=league_sos)


def scrape_ff_player_pool():
    # This loops through the FF player pages and saves the player name, id, and eligibility to the database
    from bs4 import BeautifulSoup
    import pandas as pd
    import requests
    import time
    import unidecode

    import sys
    sys.path.append('python/munging')
    import player_names
    sys.path.append('python/general')
    import postgres


    # EXTRACT
    pitcher_base_url = 'https://www.fleaflicker.com/mlb/leagues/23172/players?season=2021&statType=1&sortMode=1&position=1536&isFreeAgent=false&tableSortDirection=DESC&tableSortName=pv7&tableOffset='
    hitter_base_url  = 'https://www.fleaflicker.com/mlb/leagues/23172/players?season=2021&statType=1&sortMode=1&position=511&isFreeAgent=false&tableSortDirection=DESC&tableSortName=pv7&tableOffset='
    rp_base_url      = 'https://www.fleaflicker.com/mlb/leagues/23172/players?season=2021&statType=1&sortMode=1&position=1536&isFreeAgent=false&tableSortName=st25&tableSortDirection=DESC&tableOffset='

    players = []
    for baseurl in [hitter_base_url, pitcher_base_url, rp_base_url]:
        count_top = 601
        if baseurl in [rp_base_url]:
            count_top = 201
            
        for i in range(0, count_top, 20):
            url = baseurl + str(i)
            page = requests.get(url)
            print('Got '+url)
            time.sleep(1)
            soup = BeautifulSoup(page.text, 'html.parser')
            table = soup.find('div', {'id':'body-center-main'}).find('table')

            count = 0
            trow = table.find('thead').next_sibling
            while trow is not None and count<20:
                player_data = trow.find('div', {'class':'player'})
                player_name = unidecode.unidecode(player_data.find('a', {'class':'player-text'}).text)
                player_id = player_data.find('a', {'class':'player-text'})['href'].split('/')[-1].split('-')[-1]
                player_url = 'https://www.fleaflicker.com' + player_data.find('a')['href']
                player_elig = player_data.find('span', {'class':'position'}).text
                player_team = player_data.find('span', {'class':'player-team'}).text
                #print('  '.join([player_name, player_id, elig]))
                players.append([player_id, player_name, player_url, player_team, player_elig])
                trow = trow.next_sibling
                count = count+1

    df_players = pd.DataFrame(players, columns=['ff_id', 'ff_name', 'ff_url', 'ff_team', 'ff_elig'])
    df_players.drop_duplicates(subset=['ff_id'], inplace=True, ignore_index=True)

    # TRANSFORM
    def combine_eligibilities(row):
        ff_elig_list = row['ff_elig'].split('/')
        #print(row['ff_name'])
        #print(row['ff_elig'])
        #print(ff_elig_list)
        eligibilities = []

        # Infielders
        for pos in ['C', '1B', '2B', 'SS', '3B']:
            if pos in ff_elig_list:
                eligibilities.append(pos)
        if '2B' in eligibilities or 'SS' in eligibilities:
            eligibilities.append('MI')
        if '1B' in eligibilities or '3B' in eligibilities:
            eligibilities.append('CI')
        if 'MI' in eligibilities or 'CI' in eligibilities:
            eligibilities.append('IF')

        # Outfielders
        for pos in ['OF', 'RF', 'LF', 'CF']:
            if pos in ff_elig_list and 'OF' not in eligibilities:
                eligibilities.append('OF')

        # Pitchers - just use the same as FF
        if 'SP' in eligibilities or 'RP' in eligibilities or 'P' in eligibilities:
            eligibilities = ff_elig_list

        #print(eligibilities)
        # Concatenate into a string and return
        elig = ' '.join(eligibilities).strip()
        #print(elig)
        if elig == '':
            elig = 'UT'
        return elig

    df_players['elig'] = df_players.apply(lambda row: combine_eligibilities(row), axis=1)

    names = player_names.get_player_names()
    df_players = df_players.merge(right=names[['ff_id', 'fg_id']], how='left', on='ff_id')

    # LOAD    
    bbdb = postgres.connect_to_bbdb()
    df_players.to_sql('player_pool_ff', con=bbdb, schema='reference', if_exists='replace', chunksize=1000, method='multi', index=False)
    print('Uploaded FleaFlicker player pool')

    return df_players


# Get the FF info about a player
# Returns player name, team, and birthdate
def get_ff_player_info(ff_id):
    import dateparser
    import requests
    from bs4 import BeautifulSoup

    url_ff_player = 'https://www.fleaflicker.com/mlb/leagues/23172/players?playerId='+ff_id+'&sortMode=1'
    #print(url_ff_player)
    r = requests.get(url_ff_player)
    soup = BeautifulSoup(r.text, 'lxml')

    #print(r.url)
    soup = BeautifulSoup(r.text, 'lxml')

    link_player_info = soup.find('a', {'class':'player-text'})
    #print(link_player_info)
    player_name = link_player_info.text
    #print(player_name)

    url_player_info = 'https://www.fleaflicker.com'+link_player_info['href']
    #print(url_player_info)

    r2 = requests.get(url_player_info)
    soup2 = BeautifulSoup(r2.text, 'lxml')

    player = {}
    player['name'] = player_name

    dl_player_info = soup2.find('div', {'class':'panel-default'}).find('dl')
    dts = dl_player_info.find_all('dt')
    for dt in dts:
        #print(dt.text + ': ' + dt.nextSibling.text)
        if dt.text=='Team':
            player['team'] = dt.nextSibling.text.strip()
        if dt.text=='Age':
            player['birthdate'] = dateparser.parse(dt.nextSibling.find('span')['title']).date()

    #print(player)
    return player
