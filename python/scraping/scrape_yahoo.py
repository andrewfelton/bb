def scrape_yahoo_roster(league_num='26574'):
    import sys
    sys.path.append('python/general')
    import selenium_utilities
    import requests
    import postgres
    from bs4 import BeautifulSoup
    import pandas as pd
    sys.path.append('python/munging')
    import player_names
    import gspread
    import gspread_dataframe as gsdf

    league_url = 'https://baseball.fantasysports.yahoo.com/b1/' + league_num + '/startingrosters'
    print('Scraping from '+league_url)
    page = requests.get(league_url)
    bs_rosters = BeautifulSoup(page.text, 'html.parser')
    main_div = bs_rosters.find('div', id='yspmaincontent')
    tables = main_div.find_all('div', {'class':'Grid-u-1-2 Pend-xl'})

    rosters = []
    for table in tables:
        #roster = []
        owner = table.find('p').find('a').text
        print(owner)
        player_rows = table.find('table').find_all('tr')
        for player_row in player_rows:
            player = player_row.find('div').find('div')
            if (player!=None):
                player = player.find('a')
                print(player)
                playerid = str(player['href'].split('/')[-1])
                playername = player.text
                rosters.append([owner, playerid, playername])

    rosters = pd.DataFrame(rosters, columns=['Owner', 'yahoo_id', 'name'])


    player_names.put_missing_in_GS(id_list = rosters, type='yahoo_id')


    names = player_names.get_player_names()
    rosters = pd.merge(
        rosters[['Owner', 'yahoo_id']],
        names[['yahoo_id', 'fg_id', 'name']],
        on='yahoo_id',
        how='left'
    )
    rosters = rosters[['fg_id', 'name', 'Owner']]




    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    sh = gc.open('BB 2021 Legacy')
    gc_yahoo_rosters = sh.worksheet('SoS Legacy Rosters')
    gsdf.set_with_dataframe(gc_yahoo_rosters, rosters)



#scrape_yahoo_roster(league_num='26574')