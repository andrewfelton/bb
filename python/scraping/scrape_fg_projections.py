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
    print('Logged into FanGraphs')
    driver.get('https://www.fangraphs.com/')
    time.sleep(2)
    fg_account_name = driver.find_element_by_id('linkAccount').text
    print('Account name is: '+fg_account_name)
    time.sleep(1)
    #assert fg_account_name=='JohnnyFang'
    return driver





def scrape_fg_projections(type, system, mytype, mysystem):
    import os
    from datetime import date
    import time
    import pandas as pd
    import datetime
    import sys
    sys.path.append('python/general')
    import selenium_utilities
    sys.path.append('python/munging')
    import player_names
    from player_names import put_missing_in_GS
    import postgres
    sys.path.append('python/scraping')
    import scrape_fg_projections
    from scrape_fg_projections import fg_login

    driver = selenium_utilities.start_driver(headless=True)
    driver = fg_login(driver)

    fg_proj_url_base = 'https://www.fangraphs.com/projections.aspx?pos=all'
    fg_proj_url_type = 'stats='+type
    fg_proj_url_system = 'type='+system
    fg_proj_url = fg_proj_url_base+'&'+fg_proj_url_type+'&'+fg_proj_url_system
    driver.get(fg_proj_url)
    time.sleep(2)
    print('Arrived at '+driver.current_url)

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





def scrape_fg_leaderboard(fg_leaderboard_url, gs_name=False, tablename=False):
    import os
    from datetime import date
    import sys
    sys.path.append('python/general')
    import selenium_utilities
    sys.path.append('python/munging')
    import player_names
    from player_names import put_missing_in_GS
    import postgres
    import time
    import pandas as pd
    import datetime
    from selenium.webdriver.common.action_chains import ActionChains

    driver = selenium_utilities.start_driver(headless=False)
    driver = fg_login(driver)

    driver.get(fg_leaderboard_url)
    time.sleep(2)
    print('Arrived at '+driver.current_url)

    btn_dl_projections = driver.find_element_by_id('LeaderBoard1_cmdCSV')

    actions = ActionChains(driver)
    actions.move_to_element(btn_dl_projections).perform()
    driver.execute_script("window.scrollBy(0, 200);")

    btn_dl_projections.click()
    time.sleep(3)

    basepath = "/Users/andrewfelton/Documents/bb/bb-2021"
    dl_file = "/Users/andrewfelton/Downloads/docker/FanGraphs\ Leaderboard.csv"

    today = date.today().strftime("%Y%m%d")
    new_file = basepath + "/data/fangraphs/relievers_last14_" + today + ".csv"
    stream_command = os.popen('mv ' + dl_file + ' ' + new_file)
    mv_file = stream_command.read()

    # create the soft link
    ln_file = basepath + "/data/fangraphs/relievers_last14.csv"
    command_ln = os.popen('ln -sf ' + new_file + ' ' + ln_file)

    driver.close()
    #selenium_utilities.stop_selenium('bbsel')
    print("Finished scraping "+ ln_file)

    relievers_last14 = pd.read_csv(ln_file)
    relievers_last14.insert(0, 'asof_date', date.today().strftime('%Y-%m-%d'))
    relievers_last14.rename(columns={
        'playerid':'fg_id',
        "CSW%": "CSW_pct", "K%": "K_pct",
        "BB%": "BB_pct", "SwStr%": "SwStr_pct",
        'vFA (sc)':'vFA', 'LOB%':'LOB_pct', 'HR/FB':'HR_FB'
        }, inplace=True)
    relievers_last14[['fg_id']] = relievers_last14[['fg_id']].astype(str)
    relievers_last14.sort_values(by='WPA', ascending=False, inplace=True)

    # Check to confirm that all the fg_id are in the names table
    # To avoid pandas issues take it out of the dataframe and then put it back in
    # fg_ids = relievers_last14[['fg_id']].values
    #put_missing_in_GS(id_list=pd.DataFrame(fg_ids, columns=['fg_id']), type='fg_id')

    tablename = "relievers_last14_raw"
    bbdb = postgres.connect_to_bbdb()

    query_tables = "SELECT * FROM pg_catalog.pg_tables WHERE schemaname='tracking';"
    tables_list_result = bbdb.execute(query_tables)
    tables_list = []
    for table in tables_list_result:
        tables_list.append(table[1])

    if (tablename in tables_list):
        command = 'TRUNCATE TABLE tracking.'+tablename
        bbdb.execute(command)
    relievers_last14.to_sql(tablename, bbdb, schema='tracking', if_exists='append', index=False)

    return relievers_last14


#url = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=c%2c7%2c13%2c11%2c114%2c70%2c63%2c-1%2c6%2c224%2c62%2c122%2c332%2c-1%2c331%2c120%2c121%2c113%2c-1%2c139%2c-1%2c43%2c44%2c51&season=2021&month=2&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=2021-01-01&enddate=2021-12-31&sort=8%2cd&page=1_500'
#scrape_fg_leaderboard(fg_leaderboard_url=url)


