def login():
    import sys
    import time
    sys.path.append('/python')
    import selenium_utilities

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
    from bs4 import BeautifulSoup
    import pandas as pd
    sys.path.append('python/general')
    import postgres
    import classes
    sys.path.append('python/munging')
    import rosters
    import player_names
    import requests

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
                player_ff_id = player_data['href'].split('/')[-1].split('-')[-1]
                current_team.add_player(player_name, player_ff_id)

    df_export = pd.DataFrame(columns=['Team','Player','ff_id'])
    for team in teams:
        df_export = pd.concat([df_export, team.to_dataframe()])
    df_export.reset_index(drop=True, inplace=True)

    names = player_names.get_player_names()
    df_export = df_export.merge(right=names[['ff_id', 'fg_id']], how='left', on='ff_id')

    missing_fg_id = df_export[df_export['fg_id'].isna()]
    if len(missing_fg_id)>0:
        print('Miising fg_id for '+str(len(missing_fg_id.values))+' player(s):')
        for player in missing_fg_id.values.tolist():
            print(player)


    file_rosters = '/Users/andrewfelton/Documents/bb/2021/data/rosters/rosters_'+league_num+'_'+str_today+'.csv'
    df_export.to_csv(file_rosters, index=False)
    print('Saved rosters to ' + file_rosters)

    if upload_to_db:
        bbdb = postgres.connect_to_bbdb()
        df_export.to_sql('sos', con=bbdb, schema='rosters', if_exists='replace')
        print('Uploaded to database')

    return df_export


def team_rosters():
    import sys
    import datetime
    from bs4 import BeautifulSoup
    import pandas as pd
    sys.path.append('python/general')
    import postgres
    sys.path.append('python/munging')
    import rosters
    import player_names
    import requests

    assert(league.league_platform == 'fleaflicker')
    league_num = league.league_num


    roster_url = 'https://www.fleaflicker.com/mlb/leagues/'+league_num
    page = requests.get(roster_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    league_names_divs = soup.find_all('div', {'class':'league-name'})
    for league_names_div in league_names_divs:
        print(league_names_div)

        team_roster_url = 'https://www.fleaflicker.com' + league_name_div.find('a')['href']
        league_num = team_roster_url.split('/')[-1]
        team_roster_page = requests.get(team_roster_url)
        team_roster_soup = BeautifulSoup(page.text, 'html.parser')
        main_table = team_roster_soup.find('div', {'id': 'body-center-main'}).find('table')
        trows = main_table.find_all['tr']



