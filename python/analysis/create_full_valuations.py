def create_combined_valuations(league):

    import sys
    sys.path.append('python/utilities')
    import postgres
    import utilities
    sys.path.append('python/munging')
    import player_names
    sys.path.append('python/analysis')
    import calculations
    import create_combined
    import league_settings
    import pandas as pd
    import format_gs
    import gspread
    import gspread_dataframe as gsdf
    import gspread_formatting as gsfmt

    assert league in ['SoS', 'Legacy']
    #league = 'SoS'
    #league = 'Legacy'

    ls = league_settings.lsettings(league)
    bbdb = postgres.connect_to_bbdb()
    names = player_names.get_player_names()
    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    bb2021 = gc.open("BB 2021 " + league)

    combined_hitters = create_combined.create_combined_hitters(ls)
    combined_hitters['type']='B'

    combined_hitters['sample'] = combined_hitters.apply(lambda row: row.pa > 500, axis=1)
    for run in range(1,3):
        combined_hitters = calculations.calc_z(df=combined_hitters, ls=ls, type='hitting')
        combined_hitters['sample'] = combined_hitters.apply(lambda row: row.zar > 0, axis=1)

    columns = ['name','fg_id','type','pa',
               ls.hitting_counting_stats,
               ls.hitting_rate_stats,
               'zar','value']
    columns = utilities.flatten(columns)
    combined_hitters = combined_hitters[columns]

    hitter_projections = bb2021.worksheet('Hitter Projections')
    bb2021.values_clear(hitter_projections.title + "!A:Z")
    gsdf.set_with_dataframe(hitter_projections, combined_hitters)
    hitter_projections.update
    format_gs.format_gs_all(league=league, ls=ls, type='hitting')




    combined_pitchers = create_combined.create_combined_pitchers(ls)
    combined_pitchers['type']='P'

    if league == 'SoS':
        combined_pitchers['sample'] = combined_pitchers.apply(lambda row: row.qs > 10.0 or row.sv > 5 or row.hld > 5, axis=1)
    elif league == 'Legacy':
        combined_pitchers['sample'] = combined_pitchers.apply(lambda row: row.ip > 100.0 or row.svhld > 10, axis=1)

    for run in range(1,3):
        combined_pitchers = calculations.calc_z(df=combined_pitchers, ls=ls, type='pitching')
        combined_pitchers['sample'] = combined_pitchers.apply(lambda row: row.zar > 0, axis=1)

    columns = ['name','fg_id','team','type','elig','ip',
               ls.pitching_counting_stats,
               ls.pitching_rate_stats,
               'zar','value','zar_skills','rank_sp','rank_rp']
    columns = utilities.flatten(columns)
    combined_pitchers = combined_pitchers[columns]

    pitcher_projections = bb2021.worksheet('Pitcher Projections')
    #bb2021.values_clear(pitcher_projections.title + "!A:Z")
    gsdf.set_with_dataframe(pitcher_projections, combined_pitchers)
    pitcher_projections.update
    format_gs.format_gs_all(league=league, ls=ls, type='pitching')




    combined = pd.concat(
        [combined_hitters[['name','fg_id','type','zar','value']],
        combined_pitchers[['name','fg_id','type','zar','value']]])
    combined = combined.sort_values(by='value', ascending=False)

    gs_combined = bb2021.worksheet('Combined Z')
    gsdf.set_with_dataframe(gs_combined, combined)
    gs_combined.update

    gsfmt.format_cell_range(
        gs_combined, 'D:E',
        gsfmt.CellFormat(numberFormat=gsfmt.NumberFormat(type='NUMBER', pattern='0.0')))



#create_combined_valuations(league='SoS')
#create_combined_valuations(league='Legacy')


