def scrape_ottoneu_player_pool():
    import os
    from datetime import datetime
    from datetime import date
    from datetime import time
    import pandas as pd
    from selenium.webdriver.common.action_chains import ActionChains

    from general import selenium_utilities
    from munging import player_names
    from player_names import put_missing_in_GS
    from general import postgres

    driver = selenium_utilities.start_driver(headless=False)
    url = 'http://ottoneu.fangraphs.com/averageValues'
    driver.get(url)
    time.sleep(2)
    print('Arrived at '+driver.current_url)

    button_csv = driver.find_element_by_xpath('/html/body/main/header/div[2]/a[1]')
    button_csv.click()
    time.sleep(3)

    basepath = "/Users/andrewfelton/Documents/bb/bb-2021"
    dl_file = "/Users/andrewfelton/Downloads/docker/ottoneu_average_values.csv"

    today = date.today().strftime("%Y%m%d")
    new_file = basepath + "/data/ottoneu/ottoneu_average_values_" + today + ".csv"
    stream_command = os.popen('mv ' + dl_file + ' ' + new_file)
    mv_file = stream_command.read()

    # create the soft link
    ln_file = basepath + "/data/ottoneu/ottoneu_average_values.csv"
    command_ln = os.popen('ln -sf ' + new_file + ' ' + ln_file)

    driver.close()
    print("Finished scraping "+ ln_file)

    ottoneu_player_pool = pd.read_csv(ln_file)
    ottoneu_player_pool.insert(0, 'asof_date', date.today().strftime('%Y-%m-%d'))
    ottoneu_player_pool.rename(columns={
        'Name':'name',
        'OttoneuID':'otto_id',
        'FG MajorLeagueID':'fg_id',
        'FG MinorLeagueID':'fg_minor_id'
        }, inplace=True)
    for idtype in ['otto_id', 'fg_id', 'fg_minor_id']:
        ottoneu_player_pool[[idtype]] = ottoneu_player_pool[[idtype]].astype(str)

    tablename = "player_pool_ottoneu"
    bbdb = postgres.connect_to_bbdb()

    query_tables = "SELECT * FROM pg_catalog.pg_tables WHERE schemaname='reference';"
    tables_list_result = bbdb.execute(query_tables)
    tables_list = []
    for table in tables_list_result:
        tables_list.append(table[1])

    if (tablename in tables_list):
        command = 'TRUNCATE TABLE tracking.'+tablename
        bbdb.execute(command)
    ottoneu_player_pool[['asof_date', 'name', 'otto_id', 'fg_id', 'fg_minor_id']].to_sql(tablename, bbdb, schema='reference', if_exists='append', index=False)

    return ottoneu_player_pool


#url = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=c%2c7%2c13%2c11%2c114%2c70%2c63%2c-1%2c6%2c224%2c62%2c122%2c332%2c-1%2c331%2c120%2c121%2c113%2c-1%2c139%2c-1%2c43%2c44%2c51&season=2021&month=2&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=2021-01-01&enddate=2021-12-31&sort=8%2cd&page=1_500'
#scrape_fg_leaderboard(fg_leaderboard_url=url)


