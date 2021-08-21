def login_razz(driver):
    # Check if already logged in
    try:
        user_info = driver.find_element_by_id('wp-admin-bar-user-info')
    except NoSuchElementException:
        # If not logged in, then log in
        driver.get("https://razzball.com/wp-login.php?redirect_to=https%3A%2F%2Frazzball.com")
        input_login = driver.find_element_by_id('user_login')
        input_login.send_keys('andy.felton+razz@gmail.com')
        input_pw = driver.find_element_by_id('user_pass')
        input_pw.send_keys('36Pm4jKml7')
        input_submit = driver.find_element_by_id('wp-submit')
        input_submit.click()


def scrape_razz(mytype, url, logged_in_driver=False, merge_ownership=True):
    from bs4 import BeautifulSoup
    import pandas as pd
    from datetime import datetime
    from datetime import date
    import os
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from general import selenium_utilities
    from general import postgres
    from munging import player_names
    from munging import rosters

    print('Going to scrape '+mytype+' from '+url)

    if not logged_in_driver:
        driver = selenium_utilities.start_driver()
        waiter = WebDriverWait(driver, 10)

        # Get the home page
        driver.get("https://razzball.com/")
        #expected condition
        waiter.until(EC.presence_of_element_located((By.ID, 'sitemenu')))
        #JavaScript Executor to stop page load
        driver.execute_script("window.stop();")

        # Check if already logged in
        try:
            user_info = driver.find_element_by_id('wp-admin-bar-user-info')
        except NoSuchElementException:
            # If not logged in, then log in
            driver.get("https://razzball.com/wp-login.php?redirect_to=https%3A%2F%2Frazzball.com")
            input_login = driver.find_element_by_id('user_login')
            input_login.send_keys('andy.felton+razz@gmail.com')
            input_pw = driver.find_element_by_id('user_pass')
            input_pw.send_keys('36Pm4jKml7')
            input_submit = driver.find_element_by_id('wp-submit')
            input_submit.click()

    # Go to the projections page
    driver.get(url)
    print("Arrived at "+url)

    # Copy the csv window into BS
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.find('table', id='neorazzstatstable')
    # Close it down
    driver.close()

    streamers = []

    colnames = []
    # Get the list of column names
    ths = table.findAll('th')
    for th in ths:
        colname = th.text.lower()
        colname = colname.replace('#', 'rank').replace('$','value').replace('!','').replace('%','pct_')
        colnames.append(colname)
    # Insert Razz ID before Name
    colnames.insert(colnames.index('name'), 'razz_id')

    # Loop through all the rows and append them to the list
    trows = table.findAll('tr')
    for trow in trows:
        streamer = []
        tds = trow.findAll('td')
        append = True

        if [] == list(set(trow['class']) &
                      set(['class=sorter-head', 'tablesorter-headerRow', 'tablesorter-ignoreRow'])):
            for loc, td in enumerate(tds):
                if (loc+1)==colnames.index('name'):
                    player_url = td.find('a')['href']
                    player_id = player_url.split('/')[4]
                    player_id = '660271' if (str(player_id) == '6602710') else player_id  # Manual correction for Ohtani
                    streamer.append(player_id)  # Razz ID
                    player_name = td.find('a').text
                    streamer.append(player_name)  # player name
                elif ('date' in colnames) and (loc+1)==colnames.index('date'):
                    date_str =td.text + '/2021'
                    streamdate = datetime.strptime(date_str, '%m/%d/%Y')
                    streamer.append(streamdate) # Date
                else:
                    try:
                        value = float(td.text)
                    except ValueError:
                        value = td.text
                    streamer.append(value)

            # Some times there are entries with missing values -- do not include those in the dataframe
            for var in ['pa', 'ip']:
                if var in colnames and (
                        str(streamer[colnames.index(var)])=='' or
                        str(streamer[colnames.index(var)])=='None'
                ):
                    append = False
            if streamer[colnames.index('razz_id')]==1.0:
                append = False
            if str(streamer[colnames.index('value')])=='':
                append = False
            if append:
                streamers.append(streamer)
    df_streamers = pd.DataFrame(streamers, columns=colnames)
    df_streamers.drop(df_streamers[df_streamers['razz_id']==1.0].index, inplace=True)

    # fix date
    #date_str = tds[4].text + '/2021'
    #streamdate = datetime.strptime(date_str, '%m/%d/%Y')

    names = player_names.get_player_names()
    df_streamers = df_streamers.merge(right=names[['mlb_id', 'fg_id']], how='left', left_on='razz_id', right_on='mlb_id')
    df_streamers['fg_id'] = df_streamers.apply(lambda row: row['fg_id'] if str(row['fg_id'])!='nan' else row['razz_id'], axis=1)

    if merge_ownership:
        ff_rosters = rosters.get_ff_ownership().rename(columns={"Team": "SoS_Team"})
        legacy_rosters = rosters.get_legacy_ownership().rename(columns={"Team": "Legacy_Team"})
        df_streamers = df_streamers.merge(
            right=ff_rosters[['SoS_Team', 'fg_id']], how='left', on='fg_id').merge(
                right=legacy_rosters[['Legacy_Team', 'fg_id']], how='left', on='fg_id')

    # Save on computer as .csv file
    mysystem = 'razz'
    today = date.today().strftime("%Y%m%d")
    basename = "/Users/andrewfelton/Documents/bb/bb-2021/data/" + mysystem + '/' + mysystem + "_" + mytype
    new_file = basename + "_" + today + ".csv"
    df_streamers.to_csv(new_file)

    # create the soft link
    ln_file = basename + ".csv"
    command_ln = os.popen('ln -sf ' + new_file + ' ' + ln_file)
    print(command_ln)

    # Upload to the database
    tablename = mytype
    bbdb = postgres.connect_to_bbdb()

    query_tables = "SELECT * FROM pg_catalog.pg_tables WHERE schemaname='proj';"
    tables_list_result = bbdb.execute(query_tables)
    tables_list = []
    for table in tables_list_result:
        tables_list.append(table[1])

    if (tablename in tables_list):
        command = 'TRUNCATE TABLE proj."'+tablename+'"'
        bbdb.execute(command)
    df_streamers.to_sql(tablename, bbdb, schema='proj', if_exists='append', index=False)

    return df_streamers



# for testing
if (1==2):
    mytype='pitchers'
    url="https://razzball.com/steamer-pitcher-projections/"


#scrape_razz(mytype='pitchers', url="https://razzball.com/steamer-pitcher-projections/")
#time.sleep(2)
#scrape_razz(mytype='batters', url="https://razzball.com/steamer-hitter-projections/")

#scrape_razz(mytype='streamers', url="https://razzball.com/streamers/")
#scrape_razz(mytype='hittertron-today', url="https://razzball.com/hittertron-today/")
#scrape_razz(mytype='hittertron-tomorrow', url="https://razzball.com/hittertron-tomorrow/")

#razz_ros_pitchers = scrape_razz(mytype='razz_ros_pitchers', url="https://razzball.com/restofseason-pitcherprojections/")

