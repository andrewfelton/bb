def scrape_yahoo_roster(league_num='26574'):
    import sys
    sys.path.append('python/general')
    import postgres
    import selenium_utilities
    import requests
    import postgres
    from bs4 import BeautifulSoup
    import pandas as pd
    sys.path.append('python/munging')
    import player_names
    import gspread
    import gspread_dataframe as gsdf
    from datetime import date

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

    today = date.today().strftime("%Y%m%d")
    basename = "/Users/andrewfelton/Documents/bb/bb-2021/data/yahoo/rosters"
    new_file = basename + "_" + today + ".csv"
    rosters.to_csv(new_file)

    bbdb = postgres.connect_to_bbdb()
    rosters.to_sql('legacy', con=bbdb, schema='rosters', if_exists='replace', index=False)
    print('Uploaded to database')

#scrape_yahoo_roster(league_num='26574')