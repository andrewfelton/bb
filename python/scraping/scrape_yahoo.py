def scrape_yahoo_roster(league_num='26574'):
    print('\n--------------------------\nScraping Yahoo rosters:\n')

    from datetime import date
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    import gspread
    import gspread_dataframe as gsdf

    from general import postgres
    from general import selenium_utilities
    from munging import player_names

    league_url = 'https://baseball.fantasysports.yahoo.com/b1/' + league_num + '/startingrosters'
    print('Scraping from '+league_url)
    page = requests.get(league_url)
    bs_rosters = BeautifulSoup(page.text, 'html.parser')
    main_div = bs_rosters.find('div', id='yspmaincontent')
    tables = main_div.find_all('div', {'class':'Grid-u-1-2 Pend-xl'})

    rosters = []
    for table in tables:
        #roster = []
        owner_id = table.find('p').find('a')['href'].split('/')[-1]
        owner = table.find('p').find('a').text
        # print('Scraping ' + owner)
        player_rows = table.find('table').find('tbody').find_all('tr')
        for player_row in player_rows:
            tds = player_row.find_all('td')
            td_pos = tds[0]
            pos = td_pos.text
            td_player = tds[1]
            info_player = td_player.find('div', {'class':'ysf-player-name'})
            if info_player.find('div', {'class':'emptyplayer'}) is not None:
                rosters.append([owner, pos, 'empty', 'empty'])
            else:
                player = info_player.find('a')
                #print(player)
                playerid = str(player['href'].split('/')[-1])
                playername = player.text
                rosters.append([owner_id, owner, pos, playerid, playername])

    rosters = pd.DataFrame(rosters, columns=['owner_id', 'Team', 'pos', 'yahoo_id', 'name'])
    #player_names.put_missing_in_GS(id_list=rosters[rosters['yahoo_id']!='empty'], type='yahoo_id')


    names = player_names.get_player_names()
    rosters = rosters.merge(
        names[['yahoo_id', 'fg_id', 'name']],
        on='yahoo_id',
        how='left'
    )
    today = date.today().strftime("%Y%m%d")
    rosters['date'] = today
    rosters = rosters[['date', 'owner_id', 'Team', 'pos', 'fg_id', 'yahoo_id']]

    missing_fg_id = rosters[rosters['fg_id'].isna()]
    if len(missing_fg_id)>0:
        for player in missing_fg_id.values.tolist():
            if player[3] != 'empty': # Don't flag if it's just an empty position slot
                print('\nMissing info on:')
                print(player)
                yahoo_match = player_names.find_other_ids_w_yahoo(player[5])
        player_names.push_player_names_to_gs()
        print('Updated Google Sheets')



    today = date.today().strftime("%Y%m%d")
    basename = "/Users/andrewfelton/Documents/bb/bb-2021/data/yahoo/rosters"
    new_file = basename + "_" + today + ".csv"
    rosters.to_csv(new_file)

    bbdb = postgres.connect_to_bbdb()
    rosters.to_sql('legacy', con=bbdb, schema='rosters', if_exists='replace', index=False)
    print('Uploaded to database')

#scrape_yahoo_roster(league_num='26574')




def scrape_yahoo_player_pool():
    # This loops through the FF player pages and saves the player name, id, and eligibility to the database
    from bs4 import BeautifulSoup
    import pandas as pd
    import requests
    import time
    import unidecode

    from munging import player_names
    from general import postgres


    # EXTRACT
    pitcher_base_url = 'https://baseball.fantasysports.yahoo.com/b1/26574/players?status=ALL&pos=P&cut_type=33&stat1=S_S_2021&myteam=0&sort=R_PO&sdir=1&count='
    hitter_base_url  = 'https://baseball.fantasysports.yahoo.com/b1/26574/players?status=ALL&pos=B&cut_type=33&stat1=S_S_2021&myteam=0&sort=R_PO&sdir=1&count='
              
    players = []
    for baseurl in [hitter_base_url, pitcher_base_url]:
        for i in range(0, 401, 25):
            url = baseurl + str(i)
            page = requests.get(url)
            print('Got '+url)
            time.sleep(1)
            soup = BeautifulSoup(page.text, 'html.parser')
            table = soup.find('div', {'id':'players-table'}).find('table')

            for trow in table.find('tbody').find_all('tr'):
                player_div = trow.find('div', {'class':'ysf-player-name'})
                player_name = unidecode.unidecode(player_div.find('a').text)
                player_url = player_div.find('a')['href']
                player_id = player_url.split('/')[-1].split('-')[-1]
                player_team_elig = player_div.find('span', {'class':'Fz-xxs'}).text.split('-')
                player_team = player_team_elig[0].strip()
                player_elig = player_team_elig[1].strip()
                players.append([player_id, player_name, player_url, player_team, player_elig])

    df_players = pd.DataFrame(players, columns=['yahoo_id', 'yahoo_name', 'yahoo_url', 'yahoo_team', 'yahoo_elig'])

    # TRANSFORM
    def combine_eligibilities(row):
        yahoo_elig_list = row['yahoo_elig'].split(',')
        #print(row['ff_name'])
        #print(row['ff_elig'])
        #print(ff_elig_list)
        eligibilities = []

        # Utilty/DH-only
        if yahoo_elig_list == 'Util':
            eligibilities.append('UT')

        # Infielders
        for pos in ['C', '1B', '2B', 'SS', '3B']:
            if pos in yahoo_elig_list:
                eligibilities.append(pos)
        if '2B' in eligibilities or 'SS' in eligibilities:
            eligibilities.append('MI')
        if '1B' in eligibilities or '3B' in eligibilities:
            eligibilities.append('CI')
        if 'MI' in eligibilities or 'CI' in eligibilities:
            eligibilities.append('IF')

        # Outfielders
        for pos in ['OF', 'RF', 'LF', 'CF']:
            if pos in yahoo_elig_list and 'OF' not in eligibilities:
                eligibilities.append('OF')

        # Pitchers
        for pos in ['SP', 'RP']:
            if pos in yahoo_elig_list:
                eligibilities.append(pos)

        #print(eligibilities)
        # Concatenate into a string and return
        elig = ' '.join(eligibilities).strip()
        #print(elig)
        if elig == '':
            elig = 'UT'
        return elig

    df_players['elig'] = df_players.apply(lambda row: combine_eligibilities(row), axis=1)

    names = player_names.get_player_names()
    df_players = df_players.merge(right=names[['yahoo_id', 'fg_id']], how='left', on='yahoo_id')

    # LOAD    
    bbdb = postgres.connect_to_bbdb()
    df_players.to_sql('player_pool_yahoo', con=bbdb, schema='reference', if_exists='replace', chunksize=1000, method='multi', index=False)
    print('Uploaded Yahoo player pool')

    return df_players
