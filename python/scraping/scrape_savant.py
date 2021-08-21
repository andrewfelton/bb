def scrape_savant():

    from datetime import date
    import os
    import pandas as pd
    from general import selenium_utilities
    from general import postgres
    from munging import player_names

    driver = selenium_utilities.start_driver()
    draft_url = "https://baseballsavant.mlb.com/leaderboard/custom?year=2021&type=batter&filter=&sort=4&sortDir=desc&min=10&selections=b_total_pa,xba,xslg,woba,xwoba,xobp,xiso,wobacon,xwobacon,exit_velocity_avg,launch_angle_avg,barrel_batted_rate,hard_hit_percent,sprint_speed,&chart=false&x=xba&y=xba&r=no&chartType=beeswarm"
    driver.get(draft_url)
    print('Arrived at '+driver.current_url)

    input_dl = driver.find_element_by_id('btnCSV')
    input_dl.click()

    basepath = "/Users/andrewfelton/Documents/bb/bb-2021"
    dl_file = "/Users/andrewfelton/Downloads/docker/stats.csv"

    today = date.today().strftime("%Y%m%d")
    new_file = basepath + "/data/savant/hitter_stats_" + today + ".csv"
    stream_command = os.popen('mv ' + dl_file + ' ' + new_file)
    mv_file = stream_command.read()

    # create the soft link
    ln_file = basepath + "/data/savant/hitter_stats.csv"
    command_ln = os.popen('ln -sf ' + new_file + ' ' + ln_file)

    driver.close()
    print("Finished scraping "+ ln_file)

    savant = pd.read_csv(ln_file)
    savant.insert(0, 'asof_date', date.today().strftime('%Y-%m-%d'))


    # Merge in the player names and FG IDs
    savant.rename(columns={
        'player_id':'mlb_id'
        }, inplace=True)
    savant['mlb_id'] = savant['mlb_id'].apply(str)
    names = player_names.get_player_names()
    savant = savant.merge(right=names[['mlb_id', 'fg_id']], how='left', on='mlb_id')

    #fg_ids = savant[['fg_id']].astype(str).values
    #put_missing_in_GS(id_list=pd.DataFrame(fg_ids, columns=['fg_id']), type='fg_id')

    savant = savant[[
        'asof_date', 'fg_id', 'b_total_pa',
        'xba', 'xslg', 'woba', 'xwoba', 'xobp', 'xiso', 'wobacon', 'xwobacon',
        'exit_velocity_avg', 'launch_angle_avg', 'barrel_batted_rate',
        'hard_hit_percent', 'sprint_speed'
    ]]

    schema = 'tracking'
    tablename = 'savant'
    bbdb = postgres.connect_to_bbdb()
    savant.to_sql(tablename, bbdb, schema=schema, if_exists='replace')
