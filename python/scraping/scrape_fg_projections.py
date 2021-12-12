def fg_login(driver):
    import time
    
    driver.get("https://blogs.fangraphs.com/wp-login.php")
    input_login = driver.find_element_by_id('user_login')
    input_login.send_keys('JohnnyFang')
    input_pw = driver.find_element_by_id('user_pass')
    input_pw.send_keys('P1^nzGTY*Ew!r1')
    input_submit = driver.find_element_by_id('wp-submit')
    input_submit.click()
    time.sleep(2)
    #print('Logged into FanGraphs')
    driver.get('https://www.fangraphs.com/')
    time.sleep(2)
    fg_account_name = driver.find_element_by_id('linkAccount').text
    #print('Account name is: '+fg_account_name)
    time.sleep(1)
    #assert fg_account_name=='JohnnyFang'
    return driver





def scrape_fg_projections(type, system, mytype, mysystem):
    import os
    from datetime import date
    import time
    import pandas as pd
    from datetime import datetime
    from general import selenium_utilities
    from general import postgres
    from munging import player_names
    from player_names import put_missing_in_GS
    from scraping import scrape_fg_projections

    driver = selenium_utilities.start_driver(headless=True)
    driver = scrape_fg_projections.fg_login(driver)

    fg_proj_url_base = 'https://www.fangraphs.com/projections.aspx?pos=all'
    fg_proj_url_type = 'stats='+type
    fg_proj_url_system = 'type='+system
    fg_proj_url = fg_proj_url_base+'&'+fg_proj_url_type+'&'+fg_proj_url_system
    driver.get(fg_proj_url)
    time.sleep(2)
    #print('Arrived at '+driver.current_url)

    btn_dl_projections = driver.find_element_by_id('ProjectionBoard1_cmdCSV')
    btn_dl_projections.click()
    time.sleep(3)

    fg_account_name = driver.find_element_by_id('linkAccount').text
    print('Account name is: '+fg_account_name)


    basepath = "/Users/andrewfelton/Documents/bb/bb-2021"
    dl_file = "/Users/andrewfelton/Downloads/docker/FanGraphs\ Leaderboard.csv"

    today = date.today().strftime("%Y%m%d")
    new_file = basepath + "/data/fangraphs/" + mysystem + "_" + mytype + "_" + today + ".csv"
    stream_command = os.popen('mv ' + dl_file + ' ' + new_file)
    mv_file = stream_command.read()

    # create the soft link
    ln_file = basepath + "/data/fangraphs/" + mysystem + "_" + mytype + ".csv"
    command_ln = os.popen('ln -sf ' + new_file + ' ' + ln_file)

    driver.close()
    #selenium_utilities.stop_selenium('bbsel')
    print("Finished scraping "+ ln_file)

    proj = pd.read_csv(ln_file)
    proj.insert(0, 'asof_date', date.today().strftime('%Y-%m-%d'))

    # Check to confirm that all the fg_id are in the names table
    # To avoid pandas issues take it out of the dataframe and then put it back in
    fg_ids = proj[['playerid']].astype(str).values
    #put_missing_in_GS(id_list=pd.DataFrame(fg_ids, columns=['fg_id']), type='fg_id')

    tablename = mysystem + "_" + mytype + "_raw"
    bbdb = postgres.connect_to_bbdb()

    query_tables = "SELECT * FROM pg_catalog.pg_tables WHERE schemaname='proj';"
    tables_list_result = bbdb.execute(query_tables)
    tables_list = []
    for table in tables_list_result:
        tables_list.append(table[1])

    if (tablename in tables_list):
        command = 'TRUNCATE TABLE proj.'+tablename
        bbdb.execute(command)
    proj.to_sql(tablename, bbdb, schema='proj', if_exists='append', index=False)





def scrape_all_fg_projections():
    # Pre-season
    # scrape_fg_projections(type="bat", system="fangraphsdc", mytype="batters", mysystem="fg_dc")
    # scrape_fg_projections(type="pit", system="fangraphsdc", mytype="pitchers", mysystem="fg_dc")
    # scrape_fg_projections(type="bat", system="thebat", mytype="batters", mysystem="thebat")
    # scrape_fg_projections(type="pit", system="thebat", mytype="pitchers", mysystem="thebat")
    # scrape_fg_projections(type="bat", system="thebatx", mytype="batters", mysystem="thebatx")

    # In-season (ROS)
    scrape_fg_projections(type="bat", system="rfangraphsdc", mytype="batters", mysystem="fg_dc")
    scrape_fg_projections(type="pit", system="rfangraphsdc", mytype="pitchers", mysystem="fg_dc")
    scrape_fg_projections(type="bat", system="rthebat", mytype="batters", mysystem="thebat")
    scrape_fg_projections(type="pit", system="rthebat", mytype="pitchers", mysystem="thebat")
    scrape_fg_projections(type="bat", system="rthebatx", mytype="batters", mysystem="thebatx")


# for testing
if (1==0):
    type = "bat"
    system = "fangraphsdc"
    mytype = "batters"
    mysystem = "fg_dc"
    fg_leaderboard_url = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=c%2c7%2c13%2c11%2c114%2c70%2c63%2c-1%2c6%2c224%2c62%2c122%2c332%2c-1%2c331%2c120%2c121%2c113%2c-1%2c139%2c-1%2c43%2c44%2c51&season=2021&month=2&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=2021-01-01&enddate=2021-12-31&sort=8%2cd&page=1_500'


def scrape_fg_leaderboard(fg_leaderboard_url, scrapedate, folder, filename, schema, table, driver=None):
    import os
    from datetime import date
    import time
    import pandas as pd
    import datetime
    from selenium.webdriver.common.action_chains import ActionChains
    import yaml

    from scraping import scrape_fg_projections
    from general import selenium_utilities
    from general import postgres
    from munging import player_names

    bbdb = postgres.connect_to_bbdb()

    driver_keepalive = True
    if driver==None:
        driver_keepalive = False
        driver = selenium_utilities.start_driver(headless=False)
        driver = scrape_fg_projections.fg_login(driver)

    driver.get(fg_leaderboard_url)
    time.sleep(1)
    print('Arrived at '+driver.current_url)

    btn_dl_projections = driver.find_element_by_id('LeaderBoard1_cmdCSV')

    actions = ActionChains(driver)
    actions.move_to_element(btn_dl_projections).perform()
    driver.execute_script("window.scrollBy(0, 200);")

    btn_dl_projections.click()
    time.sleep(3)

    if not driver_keepalive:
        driver.close()
        driver.quit()

    basepath = "/Users/andrewfelton/Documents/bb/bb-2021"
    dl_file = "/Users/andrewfelton/Downloads/docker/FanGraphs\ Leaderboard.csv"

    new_file = "{basepath}/data/{folder}/{filename}_{scrapedate}.csv".format(
        basepath=basepath, folder=folder, filename=filename, scrapedate=scrapedate
    )
    stream_command = 'mv {dl_file} {new_file}'.format(
        dl_file=dl_file, new_file=new_file)
    mv_file_exec = os.popen(stream_command)
    print(mv_file_exec.read())
    print("Finished scraping "+ new_file)

    # TRANSFORM
    # Read the CSV file, convert to dataframe, remap the column headers
    stream = open('/Users/andrewfelton/Documents/bb/bb-2021/python/scraping/field_name_mapping.yml', 'r')
    mapper = yaml.load(stream, yaml.CLoader)
    fgfile = pd.read_csv(new_file)
    fgfile.insert(0, 'asof_date', scrapedate)
    for col in fgfile.columns:
        fgfile.rename(columns={col:col.lower()}, inplace=True)
    fgfile.rename(columns=mapper['fg'], inplace=True)
    fgfile[['fg_id']] = fgfile[['fg_id']].astype(str)

    # Check if the table already exists and if so, clear out the information from the scrapedate
    query_tables = "SELECT * FROM pg_catalog.pg_tables WHERE schemaname='tracking';"
    tables_list = [t for t in bbdb.execute(query_tables)]
    if (table in tables_list):
        if schema=='hist':
            command = "DELETE FROM {schema}.{table} WHERE asof_date='{scrapedate}';".format(
                schema=schema, table=table, scrapedate=scrapedate
            )
        elif schema=='tracking':
            command = 'TRUNCATE TABLE tracking.{table}'.format(table=table)
        bbdb.execute(command)

    # Load to the database
    fgfile.to_sql(name=table, con=bbdb, schema=schema, if_exists='append')
    return fgfile



def scrape_fg_daily_leaderboards():
    import datetime
    scrapedate = datetime.date.today() - datetime.timedelta(days=1)
    print('Scraping FG leaderboards for date: '+str(scrapedate))

    folder = 'fangraphs/daily_results'
    schema = 'hist'

    url_bat = 'https://www.fangraphs.com/leaders.aspx?'+\
        'pos=all&stats=bat&lg=all&qual=0&type=0&season=2021&month=1000&'+\
        'season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&'+\
        'startdate={scrapedate}&enddate={scrapedate}'.format(scrapedate=scrapedate)
    filename = 'batters'
    table = 'daily_stats_batters'
    daily_batters = scrape_fg_leaderboard(url_bat, scrapedate, folder, filename, schema, table)

    url_pit = 'https://www.fangraphs.com/leaders.aspx?'+\
        'pos=all&stats=pit&lg=all&qual=0&type=0&season=2021&month=1000&'+\
        'season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&'+\
        'startdate={scrapedate}&enddate={scrapedate}'.format(scrapedate=scrapedate)
    filename = 'pitchers'
    table = 'daily_stats_pitchers'
    daily_pitchers = scrape_fg_leaderboard(url_pit, scrapedate, folder, filename, schema, table)

    fg_leaderboard_url='https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=c%2c7%2c13%2c11%2c114%2c70%2c63%2c-1%2c6%2c224%2c62%2c122%2c332%2c-1%2c331%2c120%2c121%2c113%2c-1%2c139%2c-1%2c43%2c44%2c51&season=2021&month=2&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=2021-01-01&enddate=2021-12-31&sort=8%2cd&page=1_500'
    folder = 'fangraphs/relievers_last14'
    schema = 'tracking'
    filename = 'relievers_last14'
    table = 'relievers_last14'
    relievers = scrape_fg_leaderboard(fg_leaderboard_url, scrapedate, folder, filename, schema, table)

    fg_leaderboard_url='https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=10&type=c,4,5,6,7,8,9,10,11,12,13,14,16,17,18,19,21,22,23,37,38&season=2021&month=3&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=2021-01-01&enddate=2021-12-31&sort=6,d&page=1_500'
    folder = 'fangraphs/batters_last30'
    schema = 'tracking'
    filename = 'batters_last30'
    table = 'batters_last30'
    batters_last30 = scrape_fg_leaderboard(fg_leaderboard_url, scrapedate, folder, filename, schema, table)




def get_fg_player_info(fg_id):
    #fg_id = '2429'
    import requests
    from bs4 import BeautifulSoup
    import dateparser

    player = {}

    fg_player_url = 'http://www.fangraphs.com/statss.aspx?playerid='+fg_id
    #print(fg_player_url)
    r = requests.get(url=fg_player_url, verify=False)
    soup = BeautifulSoup(r.text, 'lxml')
    div_player_info = soup.find('div', {'class':'player-info-box-header'})
    player['name'] = div_player_info.find('div', {'class':'player-info-box-name'}).find('h1').text.strip()
    try:
        player['team'] = div_player_info.find('div', {'class':'player-info-box-name-team'}).find('a').text.strip()
    except AttributeError:
        player['team'] = div_player_info.find('div', {'class':'player-info-box-name-team'}).text.strip()

    player['birthdate'] = soup.find('tr', {'class':'player-info__bio-birthdate'}).find('td').text
    player['birthdate'] = player['birthdate'].split(' ')[0]
    player['birthdate'] = dateparser.parse(player['birthdate']).date()
    return player
