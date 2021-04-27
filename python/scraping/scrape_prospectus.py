


def scrape_bp_pitching():
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

    driver = selenium_utilities.start_driver()
    driver.get("https://www.baseballprospectus.com/leaderboards/pitching/")
    print('Arrived at '+driver.current_url)

    dl_btn = driver.find_element_by_xpath('//*[@id="app"]/div[2]/div/div[3]/div[1]/div[2]/button')
    dl_btn.click()

    today = date.today().strftime("%Y%m%d")

    basepath = "/Users/andrewfelton/Documents/bb/bb-2021"
    dl_file = "/Users/andrewfelton/Downloads/docker/bp_export_"+today+".csv"
    new_file = basepath + "/data/bp/bp_pitchers_" + today + ".csv"
    stream_command = os.popen('mv ' + dl_file + ' ' + new_file)

    # create the soft link
    ln_file = basepath + "/data/bp/bp_pitchers.csv"
    command_ln = os.popen('ln -sf ' + new_file + ' ' + ln_file)

    driver.close()
    #selenium_utilities.stop_selenium('bbsel')
    print("Finished scraping "+ ln_file)


    bp_pitchers = pd.read_csv(ln_file)
    bp_pitchers.insert(0, 'asof_date', date.today().strftime('%Y-%m-%d'))
    bp_pitchers.rename(
        columns={
            "bpid": "bp_id", "mlbid": "mlb_id",
            "IP":"IP", "DRA":"DRA",
            '+/-':'plus_minus', 'DRA-':'DRAminus',
            'Whiff%':'whiff_pct', 'K%':'k_pct', 'BB%':'bb_pct', 
            'K/9':'k9', 'BB/9':'bb9', 'HR%':'hr_pct', 'HR/9':'hr9',
            'IFFB%':'iffb_pct', 'GB%':'gb_pct', 'LD%':'ld_pct', 'FB%':'fb_pct',
            '1B':'_1B', '2B':'_2B', '3B':'_3B'
        }
        , inplace=True)
    bp_pitchers[['bp_id']] = bp_pitchers[['bp_id']].astype("string")
    bp_pitchers[['mlb_id']] = bp_pitchers[['mlb_id']].astype("string")

    names = player_names.get_player_names()
    bp_pitchers = bp_pitchers.merge(names[['mlb_id', 'fg_id']], on='mlb_id', how='left')

    tablename = "bp_pitchers_raw"
    bbdb = postgres.connect_to_bbdb()

    query_tables = "SELECT * FROM pg_catalog.pg_tables WHERE schemaname='hist';"
    tables_list_result = bbdb.execute(query_tables)
    tables_list = []
    for table in tables_list_result:
        tables_list.append(table[1])

    if (tablename in tables_list):
        command = 'TRUNCATE TABLE hist.'+tablename
        bbdb.execute(command)
    bp_pitchers[['fg_id', 'bp_id', 'IP', 'DRA', 'cFIP']]\
        .to_sql(tablename, bbdb, schema='hist', if_exists='append', index=False)
