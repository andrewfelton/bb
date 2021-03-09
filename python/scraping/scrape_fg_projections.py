
def scrape_fg_projections(type, system, mytype, mysystem):
    import os
    from datetime import date
    import sys
    sys.path.append('python/utilities')
    import selenium_utilities
    import postgres
    import time
    import pandas as pd
    import datetime

    driver = selenium_utilities.start_driver()
    driver.get("https://blogs.fangraphs.com/wp-login.php")
    time.sleep(2)
    print('Arrived at '+driver.current_url)

    input_login = driver.find_element_by_id('user_login')
    input_login.send_keys('JohnnyFang')
    input_pw = driver.find_element_by_id('user_pass')
    input_pw.send_keys('P1^nzGTY*Ew!r1')
    input_submit = driver.find_element_by_id('wp-submit')
    input_submit.click()
    time.sleep(2)

    fg_proj_url_base = 'https://www.fangraphs.com/projections.aspx?pos=all'
    fg_proj_url_type = 'stats='+type
    fg_proj_url_system = 'type='+system
    fg_proj_url = fg_proj_url_base+'&'+fg_proj_url_type+'&'+fg_proj_url_system

    driver.get(fg_proj_url)
    time.sleep(2)
    print('Arrived at '+driver.current_url)


    fg_account_name = driver.find_element_by_id('linkAccount').text
    assert fg_account_name=='JohnnyFang'


    btn_dl_projections = driver.find_element_by_id('ProjectionBoard1_cmdCSV')
    btn_dl_projections.click()
    time.sleep(3)

    basepath = "/Users/andrewfelton/Documents/bb/2021"
    dl_file = "/Users/andrewfelton/Downloads/docker/FanGraphs\ Leaderboard.csv"

    today = date.today().strftime("%Y%m%d")
    new_file = basepath + "/data/" + mysystem + "_" + mytype + "_" + today + ".csv"
    stream_command = os.popen('mv ' + dl_file + ' ' + new_file)
    mv_file = stream_command.read()

    # create the soft link
    ln_file = basepath + "/data/" + mysystem + "_" + mytype + ".csv"
    command_ln = os.popen('ln -sf ' + new_file + ' ' + ln_file)

    driver.close()
    selenium_utilities.stop_selenium('bbsel')
    print("Finished scraping "+ ln_file)


    proj = pd.read_csv(ln_file)
    proj.insert(0, 'asof_date', date.today().strftime('%Y-%m-%d'))

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
    proj.to_sql(tablename, bbdb, schema='proj', if_exists='append')


def scrape_all_fg_projections():
    scrape_fg_projections(type="bat", system="fangraphsdc", mytype="batters", mysystem="fg_dc")
    scrape_fg_projections(type="pit", system="fangraphsdc", mytype="pitchers", mysystem="fg_dc")
    scrape_fg_projections(type="bat", system="thebat", mytype="batters", mysystem="thebat")
    scrape_fg_projections(type="pit", system="thebat", mytype="pitchers", mysystem="thebat")
    scrape_fg_projections(type="bat", system="thebatx", mytype="batters", mysystem="thebatx")

# for testing
if (1==0):
    type = "bat"
    system = "fangraphsdc"
    mytype = "batters"
    mysystem = "fg_dc"






