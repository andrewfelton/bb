

def scrape_mlb_player_pool():
    # This loops through the MLB player pages and saves the player name, id, and eligibility to the database
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
    import selenium_utilities


    # EXTRACT
    url_mlb_players = 'https://www.mlb.com/players'

    driver = selenium_utilities.start_driver(headless=True)
    driver.get(url_mlb_players)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    player_items = soup.find('div', {'id':'players-index'}).find_all('li')

    players = []
    for player_data in player_items:
        player_name = unidecode.unidecode(player_data.find('a', {'class':'p-related-links__link'}).text)
        player_url = 'https://www.mlb.com' + player_data.find('a')['href']
        player_id = player_url.split('-')[-1]
        players.append([player_id, player_name, player_url])

    df_players = pd.DataFrame(players, columns=['mlb_id', 'mlb_name', 'mlb_url'])

    names = player_names.get_player_names()
    df_players = df_players.merge(right=names[['mlb_id', 'fg_id']], how='left', on='mlb_id')

    # LOAD    
    bbdb = postgres.connect_to_bbdb()
    df_players.to_sql('player_pool_mlb', con=bbdb, schema='reference', if_exists='replace', chunksize=1000, method='multi', index=False)
    print('Uploaded MLB player pool')

    return df_players
