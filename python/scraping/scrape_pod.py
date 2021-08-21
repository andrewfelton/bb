def scrape_pod():
    import pandas as pd
    from general import postgres
    from munging import player_names

    bbdb = postgres.connect_to_bbdb()
    names = player_names.get_player_names()

    # -------------------------------
    # EXTRACT
    # -------------------------------
    pod_file_path = '/Users/andrewfelton/Documents/bb/2021/data/pod/pod_projections.xlsx'
    pod_hitters = pd.read_excel(
        pod_file_path,
        sheet_name='Hitter Projections',
        names=['Name', 'fg_id', 'Age', 'Lg', 'TM', 'Position', 'Lineup Spot',
            'G', 'AB', 'PA', 'HITS', '1B', '2B', '3B', 'HR', 'R', 'RBI',
            'BB', 'IBB', 'SO', 'HBP', 'SF', 'SB', 'CS', 'AVG', 'OBP', 'SLG',
            'OPS', 'ISO', 'wOBA', 'BB_PCT', 'K_PCT', 'BABIP', 'GB_PCT',
            'LD_PCT', 'FB_PCT', 'HR_FB']
    )

    # -------------------------------
    # TRANSFORM
    # -------------------------------
    for c in ['Name', 'fg_id', 'Age', 'Lg', 'TM', 'Position', 'Lineup Spot']:
        pod_hitters[c] = pod_hitters[c].astype(str)

    # Check to confirm that all the fg_id are in the names table
    put_missing_in_GS(pod_hitters[['fg_id']], 'fg_id')

    # -------------------------------
    # LOAD
    # -------------------------------

    command = 'TRUNCATE TABLE proj.pod_batters_raw'
    bbdb.execute(command)
    pod_hitters.to_sql('pod_batters_raw', bbdb, schema='proj', if_exists='append')
    print('Uploaded pod_batters to the database')



    pod_file_path = '/Users/andrewfelton/Documents/bb/2021/data/pod/pod_projections.xlsx'
    pod_pitchers = pd.read_excel(
        pod_file_path,
        sheet_name='Pitcher Projections')
    pod_pitchers = pd.read_excel(
        pod_file_path,
        sheet_name='Pitcher Projections',
        names=['Name', 'fg_id', 'Age', 'Lg', 'TM', 'Role', 'GS', 'IP', 'IP S', 'W',
        'L', 'QS', 'SV', 'ERA', 'H', 'R', 'ER', 'HR', 'SO', 'BB', 'HBP', 'K_9',
        'BB_9', 'HR_9', 'K_PCT', 'BB_PCT', 'BAA', 'WHIP', 'BABIP', 'LOB_PCT', 'GB_PCT',
        'LD_PCT', 'FB_PCT', 'HR_FB']
    )
    for c in ['Name', 'fg_id']:
        pod_pitchers[c] = pod_pitchers[c].astype(str)

    # Check to confirm that all the fg_id are in the names table
    put_missing_in_GS(pod_pitchers[['fg_id']], 'fg_id')

    command = 'TRUNCATE TABLE proj.pod_pitchers_raw'
    bbdb.execute(command)
    pod_pitchers.to_sql('pod_pitchers_raw', bbdb, schema='proj', if_exists='append')
    print('Uploaded pod_pitchers to the database')


scrape_pod()
