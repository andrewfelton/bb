def get_player_names():
    import pandas as pd
    from general import postgres
    
    bbdb = postgres.connect_to_bbdb()
    names = pd.read_sql_query(sql='SELECT * FROM REFERENCE.PLAYER_NAMES', con=bbdb)
    for col in ['otto_id', 'yahoo_id', 'bp_id', 'espn_id', 'ff_id', 'fg_id']:
        names[col] = names[col].astype('str').replace('\.0', '', regex=True)
    return names

def scrape_sfb_names():
    # Download the latest .csv file from smartfantasybaseball.com

    driver = selenium_utilities.start_driver()
    driver.get("https://www.smartfantasybaseball.com/PLAYERIDMAPCSV")

    filename = '/Users/andrewfelton/Downloads/docker/SFBB Player ID Map - PLAYERIDMAP.csv'
    player_names = pd.read_csv(filename)
    os.remove(filename)

    tablename = 'player_names_sfb'
    bbdb = postgres.connect_to_bbdb()
    command = 'TRUNCATE TABLE reference.' + tablename
    bbdb.execute(command)
    player_names.to_sql(tablename, bbdb, schema='reference', if_exists='append')
    player_names['yahoo_id'] = str(player_names['yahoo_id'])

def put_missing_in_GS(id_list, type):
    names = player_names.get_player_names()
    missing = []
    missing = id_list[id_list[type].isin(names[type])==False][[type]]

    if (len(missing)>0):
        gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
        sh = gc.open("BB 2021 Name Matching").worksheet('Missing from DB')
        gsdf.set_with_dataframe(sh, missing)
        print('Put '+str(len(missing))+' '+str(type)+' ids in the Google Sheet!')
        print(str(sh.spreadsheet.url)+'/edit#gid='+str(sh.id))
    else:
        print('No missing ids')

def push_player_names_to_gs():
    import pandas as pd
    import gspread
    import gspread_dataframe as gsdf

    from general import postgres

    bbdb = postgres.connect_to_bbdb()
    player_names = pd.read_sql('SELECT * FROM reference.player_names ORDER BY name', con=bbdb)
    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    sh = gc.open("BB 2021 Name Matching").worksheet('Player Names')
    gsdf.set_with_dataframe(sh, player_names)
    sh.clear_basic_filter()
    sh.set_basic_filter()

def pull_player_names_from_gs():
    import pandas as pd
    import gspread
    import gspread_dataframe as gsdf

    from general import postgres

    bbdb = postgres.connect_to_bbdb()
    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    sh = gc.open("BB 2021 Name Matching").worksheet('Player Names')
    player_names = gsdf.get_as_dataframe(sh)
    player_names.sort_values(by='name', inplace=True)

    # convert any numeric ids into text
    for col in ['fg_id', 'fg_minor_id', 'bbref_id', 'otto_id', 'yahoo_id', 'bp_id', 'espn_id', 'ff_id', 'mlb_id']:
        if col in player_names.columns:
            player_names[col] = player_names[col].astype('str').replace('\.0', '', regex=True)
            player_names[col] = player_names[col].astype('str').replace('nan', '', regex=True)
            player_names[col] = player_names[col].astype('str').replace('NaN', '', regex=True)
            

    colnames = player_names.columns.tolist()
    player_names.columns = colnames

    command = 'TRUNCATE TABLE reference.player_names'
    bbdb.execute(command)
    player_names.to_sql('player_names', bbdb, schema='reference', if_exists='append', chunksize=1000, method='multi', index=False)

def scrape_sfb_names():
    import time
    import os
    import sys
    import pandas as pd
    sys.path.append('python/general')
    import selenium_utilities
    import postgres
    

    # EXTRACT
    # Download the latest .csv file from smartfantasybaseball.com
    driver = selenium_utilities.start_driver()
    driver.get("https://www.smartfantasybaseball.com/PLAYERIDMAPCSV")
    time.sleep(2)
    filename = '/Users/andrewfelton/Downloads/docker/SFBB Player ID Map - PLAYERIDMAP.csv'
    sfb_names = pd.read_csv(filename, dtype=str)
    os.remove(filename)

    # TRANSFORM
    orignames = list(sfb_names.columns.values)
    colnames = list(sfb_names.columns.values)
    colmap = dict()
    for i in range(0, len(colnames)):
        colnames[i] = colnames[i].lower()
        if colnames[i][-2:]=='id':
            colnames[i] = colnames[i][:-2]+'_id'
        if colnames[i][:2]=='id':
            colnames[i] = colnames[i][2:]+'_id'
        if colnames[i][-4:]=='name':
            colnames[i] = colnames[i][:-4]+'_name'
        colnames[i] = colnames[i].replace('fangraphs','fg')
        colmap[orignames[i]] = colnames[i]
    sfb_names = sfb_names.rename(mapper=colmap, axis=1)

    # LOAD
    tablename = 'player_names_sfb'
    bbdb = postgres.connect_to_bbdb()
    command = 'TRUNCATE TABLE reference.' + tablename
    bbdb.execute(command)
    sfb_names.to_sql(tablename, bbdb, schema='reference', if_exists='append')

    return sfb_names

def update_master_names_list_w_sfb():
    import time
    import os
    import sys
    import pandas as pd
    sys.path.append('python/general')
    import selenium_utilities
    import postgres

    sfb_names = player_names.scrape_sfb_names()
    db_names = player_names.get_player_names()

# Gets summary player info from FG page
def get_fg_info(fg_id):
    import requests
    from bs4 import BeautifulSoup
    #fg_id = '25379'
    fg_id_url = 'http://www.fangraphs.com/statss.aspx?playerid='+str(fg_id)
    page = requests.get(fg_id_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    player_info_box = soup.find('div', attrs={'class':'player-info-box-name'})
    player_name = player_info_box.find('h1').text.strip()
    player_team = player_info_box.find('div', attrs={'class':'player-info-box-name-team'}).text.strip()
    
    return [fg_id, player_name, player_team]

# Gets summary player info from Yahoo page
def get_yahoo_info(yahoo_id):
    import requests
    from bs4 import BeautifulSoup
    #yahoo_id = '9506'
    yahoo_id_url = 'https://sports.yahoo.com/mlb/players/'+str(yahoo_id)
    page = requests.get(yahoo_id_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    player_info_box = soup.find('div', attrs={'class':'IbBox Whs(n)'})
    player_name = player_info_box.find('span', attrs={'class':'ys-name'}).text.strip()
    player_team = player_info_box.find('div', attrs={'class':'D(ib)'}).text.strip()
    
    return [yahoo_id, player_name, player_team]

# Takes a Fleaflicker ID and tries to match.  If it finds a match, asks user
# if you want to update player_names
def find_other_ids_w_ff(ff_id):
    import pandas as pd
    from general import postgres
    from munging import player_names
    from scraping import scrape_fg_projections
    from scraping import scrape_ff

    bbdb = postgres.connect_to_bbdb()

    # First, check to see if the FleaFlicker ID is even in the FF player pool
    # If not, rerun the player pool generator
    ff_sql = 'SELECT ff_id, ff_name, ff_team, ff_elig, fg_id FROM REFERENCE.player_pool_ff WHERE ff_id=\''+str(ff_id)+'\''
    ff_info = pd.read_sql_query(ff_sql, con=bbdb)
    if len(ff_info)==0:
        print('This ff_id is not in the FF player pool.  Please rerun the player pool generator update_player_pools.py')
        return False

    ff_name = ff_info['ff_name'].to_list()[0]
    print(ff_name + ' is in the Fleaflicker player pool.  Here is the info available:')
    ff_player_info = scrape_ff.get_ff_player_info(ff_id)
    print(ff_player_info)

    # Second, if it's in the FF player pool, get the best FG match for it based on name
    best_fg_match = player_names.get_fg_id_from_ff_id(ff_id)
    print('Here is the best match in the existing FanGraphs player pool')
    fg_id_tentative = best_fg_match['fg_id']
    best_fg_match = scrape_fg_projections.get_fg_player_info(fg_id_tentative)
    best_fg_match

    if ff_player_info['team']==best_fg_match['team'] and ff_player_info['birthdate']==best_fg_match['birthdate']:
        print('Looks like there is a perfect match!')
        perform_merge = input('Do you want to merge in the FleaFlicker ID into the existing match?')
        if perform_merge:
            sql_update = 'UPDATE reference.player_names ' +\
                        'SET ff_id = \''+str(ff_id)+'\'' +\
                        'WHERE fg_id=\''+str(fg_id_tentative)+'\''
            print(sql_update)
            bbdb.execute(sql_update)
            player_names.push_player_names_to_gs()
        else:
            print('OK, won\'t update')
    else:
        # If it's not already in the list of player names, see if there is a match in the raw FG data
        ff_sql = \
            'SELECT name, fg_id FROM '+\
            '(SELECT "Name" as name, playerid as fg_id from proj.fg_dc_batters_raw '+\
            'UNION '+\
            'SELECT "Name" as name, playerid as fg_id from proj.fg_dc_pitchers_raw '+\
            ') fg_raw_proj_union '+\
            'WHERE fg_id NOT IN (SELECT fg_id FROM reference.player_names) ORDER BY name'
        ff_info = pd.read_sql_query(ff_sql, con=bbdb)
        if ff_name in ff_info['name'].to_list():
            matches = ff_info[ff_info['name']==ff_name]
            if len(matches)==1:
                print('Found a match!')
                print('FG info:')
                fg_id = matches['fg_id'].to_list()[0]
                fg_info = get_fg_info(fg_id)
                print(fg_info)
                perform_append = input('Do you want to append this to the list of player names?')
                if perform_append=='Y':
                    sql_append_new_name = \
                        'INSERT INTO reference.player_names (name, fg_id, ff_id) '+\
                        'VALUES ('+\
                        '\'' + fg_info[1] + '\', \'' + str(fg_info[0]) + '\', \'' + str(ff_id) + '\'' +\
                        ')'
                    print(sql_append_new_name)
                    bbdb.execute(sql_append_new_name)
                    player_names.push_player_names_to_gs()
                else:
                    print('OK, won\'t update')
            else:
                'Cannot find an exact name match in the FG projections'

# This gets the best-matching FG id given a FF id
def get_fg_id_from_ff_id(ff_id):
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process

    from scraping import scrape_ff
    from munging import player_names

    # Get FF info on a player
    player = scrape_ff.get_ff_player_info(ff_id)
    #print('Searching for a match for '+player['name'] + ' in the FanGraphs player list')
    #print(player)

    # Find the best match for the name in the FF player pool
    names = player_names.get_player_names()
    bestmatch = process.extract(player['name'], names['name'], limit=1, scorer=fuzz.token_sort_ratio)
    name, fuzzratio, row = bestmatch[0]
    player_rostered = names.loc[row]
    return player_rostered.to_dict()


# This gets the best-matching FG id given a FF id
def get_mlb_id_from_ff_id(ff_id):
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process

    from scraping import scrape_ff

    # Get FF info on a player
    player = scrape_ff.get_ff_player_info(ff_id)
    print('Fleaflicker player name is '+player['name'])

    # Find the best match for the name in the MLB player pool
    names_mlb = pd.read_sql_query(sql='SELECT * FROM REFERENCE.player_pool_mlb', con=bbdb)
    bestmatch = process.extract(player['name'], names_mlb['mlb_name'], limit=1, scorer=fuzz.token_sort_ratio)
    name, fuzzratio, row = bestmatch[0]
    player_mlb = names_mlb.loc[row]
    #print(player_mlb)
    print('MLB player best match is '+player_mlb[1])
    return player_mlb[0]


def append_new_fg_to_names():
    import sys
    sys.path.append('python/general')
    import postgres
    sys.path.append('python/munging')
    import player_names
    import pandas as pd

    bbdb = postgres.connect_to_bbdb()
    ff_sql = 'SELECT name, playerid as fg_id, pa FROM proj.fg_dc_batters_raw WHERE playerid NOT IN (SELECT fg_id AS playerrid FROM reference.player_names) ORDER BY pa DESC'
    ff_info = pd.read_sql_query(ff_sql, con=bbdb)
    print('Find matches for this player:')


    # Check to see if they are a call-up (whether they match an existing name with a minor-league fg_id staring with 'sa')

# Takes a Yahoo ID and tries to match.  If it finds a match, asks user
# if you want to update player_names
def find_other_ids_w_yahoo(yahoo_id):
    #yahoo_id = 11702
    import sys
    sys.path.append('python/general')
    import postgres
    sys.path.append('python/munging')
    import player_names
    import pandas as pd

    bbdb = postgres.connect_to_bbdb()
    yahoo_sql = 'SELECT yahoo_id, yahoo_name, yahoo_team, yahoo_elig, fg_id FROM REFERENCE.player_pool_yahoo WHERE yahoo_id=\''+str(yahoo_id)+'\''
    yahoo_info = pd.read_sql_query(yahoo_sql, con=bbdb)
    #print('Find matches for this player:')
    #print(yahoo_info)
    
    if len(yahoo_info)==0:
        print('This yahoo_id is not in the Yahoo player pool.  Please rerun the player pool generator')
        return False
    else:
        yahoo_name = yahoo_info['yahoo_name'].to_list()[0]
        print('Here is the Yahoo player pool info available on '+yahoo_name+':')
        print(yahoo_info)

    names = player_names.get_player_names()

    # If it's already in the list of player names:
    if yahoo_name in names['name'].to_list():
        matches = names[names['name']==yahoo_name]
        if len(matches)==1:
            print('Found a match!')
            print('FG info:')
            fg_id = matches['fg_id'].to_list()[0]
            fg_info = get_fg_info(fg_id)
            print(fg_info)
            perform_merge = input('Do you want to merge in the Yahoo ID into the existing match?')
            if perform_merge:
                sql_update = 'UPDATE reference.player_names SET yahoo_id = \''+\
                    str(yahoo_id)+\
                    '\' WHERE fg_id=\''+\
                    str(fg_id)+'\''
                print(sql_update)
                bbdb.execute(sql_update)
                player_names.push_player_names_to_gs()
            else:
                print('OK, won\'t update')
        elif len(matches)>1:
            print('There is more than one match.  Please manually update.  List of matches:')
            print(matches)
    else:
        # If it's not already in the list of player names, see if there is a match in the raw FG data
        yahoo_sql = \
            'SELECT name, fg_id FROM '+\
            '(SELECT "Name" as name, playerid as fg_id from proj.fg_dc_batters_raw '+\
            'UNION '+\
            'SELECT "Name" as name, playerid as fg_id from proj.fg_dc_pitchers_raw '+\
            ') fg_raw_proj_union '+\
            'WHERE fg_id NOT IN (SELECT fg_id FROM reference.player_names) ORDER BY name'
        yahoo_info = pd.read_sql_query(yahoo_sql, con=bbdb)
        if yahoo_name in yahoo_info['name'].to_list():
            matches = yahoo_info[yahoo_info['name']==yahoo_name]
            if len(matches)==1:
                print('Found a match!')
                print('FG info:')
                fg_id = matches['fg_id'].to_list()[0]
                fg_info = get_fg_info(fg_id)
                print(fg_info)
                perform_append = input('Do you want to append this to the list of player names?')
                if perform_append=='Y':
                    sql_append_new_name = \
                        'INSERT INTO reference.player_names (name, fg_id, yahoo_id) '+\
                        'VALUES ('+\
                        '\'' + fg_info[1] + '\', \'' + str(fg_info[0]) + '\', \'' + str(yahoo_id) + '\'' +\
                        ')'
                    print(sql_append_new_name)
                    bbdb.execute(sql_append_new_name)
                    player_names.push_player_names_to_gs()
                else:
                    print('OK, won\'t update')
            else:
                'Cannot find an exact name match in the FG projections'

# This function tries to populate missing Yahoo IDs in player_names
def populate_yahoo():
    bbdb = postgres.connect_to_bbdb()

    sql = 'SELECT fg_id, name FROM reference.player_names WHERE yahoo_id = \'\''
    missing_yahoo = pd.read_sql_query(sql, con=bbdb)

    sql = 'SELECT yahoo_id, yahoo_name FROM reference.player_pool_yahoo'
    yahoo_names = pd.read_sql_query(sql, con=bbdb)

    #yahoo_search = missing_yahoo.loc[1,:].to_list()
    for i in range(len(missing_yahoo)):
        yahoo_search = missing_yahoo.loc[i, :].to_list()
        fg_id = yahoo_search[0]
        fg_name = yahoo_search[1]

        print('Looking for '+fg_name)

        if fg_name in yahoo_names['yahoo_name'].to_list():
            print('Think we found a match for '+fg_name)
            yahoo_id = yahoo_names[yahoo_names['yahoo_name']==fg_name]['yahoo_id'].values[0]
            print('FG info:')
            print(player_names.get_fg_info(fg_id))
            print('Yahoo info:')
            print(player_names.get_yahoo_info(yahoo_id))

            update = input('Go ahead and update player names (Y/N): ')
            if update=='Y':
                sql_update = 'UPDATE reference.player_names SET yahoo_id = \''+\
                    str(yahoo_id)+\
                    '\' WHERE fg_id=\''+\
                    str(fg_id)+'\''
                print(sql_update)
                bbdb.execute(sql_update)
    player_names.push_player_names_to_gs()



# This updates reference.player_bios with someone's birthday by querying fangraphs
# given their fg_id
# Returns player_info, result.rowcount
def insert_birthday(fg_id):
    import datetime
    from scraping import scrape_fg_projections

    # First check to make sure the fg_id is valid
    try:
        player_info = scrape_fg_projections.get_fg_player_info(fg_id)
    except AttributeError:
        print('There is an error finding fg_id '+fg_id+' on FanGraphs')


    # Then make sure it's in the database
    check_fg_id_exists = """
        SELECT count(fg_id) FROM reference.player_bios 
        WHERE fg_id = '{}'
        """.format(fg_id)
    result = bbdb.execute(check_fg_id_exists)


    # Then make sure it's in the database
    check_fg_id_exists = """
        SELECT fg_id, count(fg_id) as num_fg_id FROM reference.player_bios 
        WHERE fg_id = '{}'
        GROUP BY fg_id
        """.format(fg_id)
    results = bbdb.execute(check_fg_id_exists)
    if results.rowcount==0:
        insert_fg_id = """
            INSERT INTO reference.player_bios (fg_id)
            VALUES ('{}')
            """.format(fg_id)
        insert_results = bbdb.execute
        if insert_results.rowcount==0:
            print('Error!  Please check')

    # Now that we are confident the player is in the list, update his birthdate
    str_birthdate = str(player_info['birthdate'])
    update_birthdate_sql = """
        UPDATE reference.player_bios 
        SET birthdate = '{}'
        WHERE fg_id = '{}'
        """.format(str_birthdate, fg_id)
    result = bbdb.execute(update_birthdate_sql)
    return player_info, result.rowcount



