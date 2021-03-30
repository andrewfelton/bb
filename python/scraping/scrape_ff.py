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


def rosters(ls):
    import sys
    import datetime
    import re
    from bs4 import BeautifulSoup
    import pandas as pd
    sys.path.append('python/utilities')
    sys.path.append('python/munging')
    import rosters
    import player_names
    import requests

    assert(ls.league_platform == 'fleaflicker')
    league_num = ls.league_num

    roster_url = 'https://www.fleaflicker.com/mlb/leagues/'+league_num+'/teams'
    page = requests.get(roster_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    main_div = soup.find('div', id='body-center-main')
    tables = main_div.find_all('table')

    today = datetime.date.today()
    str_today = str(today)

    teams = []

    for t in tables:
        # The first team's name is in the thead, the rest are in tbody
        thead = t.find('thead')
        team_name = thead.find("span", class_="league-name").text
        teams.append(rosters.FantasyTeam(team_name))
        current_team = teams[-1]

        # Loop through the tbody
        tbody = t.find('tbody')
        trows = tbody.find_all('tr')

        for tr in trows:
            if (tr.find("span", {"class": "league-name"})): # Found the span with the team name
                team_name = tr.find("span", {"class": "league-name"}).text
                print('New team: '+team_name)
                teams.append(rosters.FantasyTeam(team_name))
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
    df_export = df_export.merge(right=names, how='left', on='ff_id')


    file_rosters = '/Users/andrewfelton/Documents/bb/2021/data/rosters/rosters_'+league_num+'_'+str_today+'.csv'
    print('Saving rosters to ' + file_rosters)
    df_export.to_csv(file_rosters, index=False)
