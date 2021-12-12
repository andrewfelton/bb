def create_combined_hitters(ls, pa=0):
    import pandas as pd
    from general import utilities
    from general import postgres
    from munging import player_names

    bbdb = postgres.connect_to_bbdb()
    query = (
            'SELECT proj.* FROM (' +
            'SELECT \'fg_dc\' as source, fg_id, pa, hr_pa, r_pa, rbi_pa, sb_pa, obp, ops ' +
            'FROM proj.fg_dc_batters ' +
            'UNION ' +
            'SELECT \'thebat\' as source, fg_id, pa, hr_pa, r_pa, rbi_pa, sb_pa, obp, ops ' +
            'FROM proj.thebat_batters ' +
            'UNION ' +
            'SELECT \'thebatx\' as source, fg_id, pa, hr_pa, r_pa, rbi_pa, sb_pa, obp, ops ' +
            'FROM proj.thebatx_batters ' +
            'UNION ' +
            'SELECT \'pod\' as source, fg_id, pa, hr_pa, r_pa, rbi_pa, sb_pa, obp, ops ' +
            'FROM proj.pod_batters ' +
            ') AS proj'
    )
    df = pd.read_sql_query(query, bbdb)

    query_pa = (
            'SELECT proj.* FROM (' +
            'SELECT \'fg_dc\' as source, fg_id, pa ' +
            'FROM proj.fg_dc_batters ' +
            #'UNION ' +
            #'SELECT \'pod\' as source, fg_id, pa ' +
            #'FROM proj.pod_batters ' +
            ') AS proj'
    )
    df_pa = pd.read_sql_query(query_pa, bbdb)
    df_pa.loc[df_pa['fg_id'] == 'sa3011918', 'fg_id'] = '27506'

    query_teams = 'SELECT playerid as fg_id, fg_dc_batters_raw."Team" as team FROM proj.fg_dc_batters_raw'
    df_teams = pd.read_sql_query(query_teams, bbdb)
    df_teams.loc[df_teams['fg_id'] == 'sa3011918', 'fg_id'] = '27506'

    weights = {'system': ['fg_dc', 'thebat', 'thebatx', 'pod'],
               'sys_weight': [1, 1, 1.2, .6]}
    weights = pd.DataFrame(weights)
    df = df.merge(right=weights, how='left', left_on='source', right_on='system')

    weights_pa = {'system': ['fg_dc', 'pod'],
               'sys_weight': [1, 0]}
    weights_pa = pd.DataFrame(weights_pa)
    df_pa = df_pa.merge(right=weights_pa, how='left', left_on='source', right_on='system')

    def weighted_average(df,data_col,weight_col,by_col):
        df['_data_times_weight'] = df[data_col]*df[weight_col]
        df['_weight_where_notnull'] = df[weight_col]*pd.notnull(df[data_col])
        g = df.groupby(by_col)
        result = g['_data_times_weight'].sum() / g['_weight_where_notnull'].sum()
        del df['_data_times_weight'], df['_weight_where_notnull']
        result = pd.DataFrame(result, columns=[data_col])
        return result



    combined_hitters = pd.DataFrame(df_pa['fg_id'].unique(), columns=['fg_id'])
    for stat in ['pa']:
        t = weighted_average(df_pa, stat, 'sys_weight', 'fg_id')
        combined_hitters = combined_hitters.merge(t, on='fg_id')
        if (pa>0):
            combined_hitters['pa'] = pa

    stats_pa = []
    for stat in ls.hitting_counting_stats:
        stats_pa.append(stat+'_pa')

    for stat in utilities.flatten([stats_pa, ls.hitting_rate_stats]):
        t = weighted_average(df, stat, 'sys_weight', 'fg_id')
        combined_hitters = combined_hitters.merge(t, on='fg_id')

    for stat in ls.hitting_counting_stats:
        stat_pa = stat+'_pa'
        combined_hitters[stat] = combined_hitters[stat_pa] * combined_hitters['pa']
        combined_hitters = combined_hitters.drop(columns=[stat_pa])


    # merge in the names and reorder
    names = player_names.get_player_names()
    combined_hitters = combined_hitters.merge(names[['fg_id', 'name']], on='fg_id', how='left')
    combined_hitters = combined_hitters.merge(df_teams, on='fg_id', how='left')
    output_stats = utilities.flatten([['fg_id', 'name', 'team', 'pa'],[ls.hitting_stats]])
    combined_hitters = combined_hitters[output_stats]

    return combined_hitters


def create_combined_pitchers(ls):
    import pandas as pd
    from munging import player_names
    from general import postgres, utilities

    bbdb = postgres.connect_to_bbdb()

    query = (
            'SELECT \'razz\' as source, fg_id, ip, qs, era, whip, k as so, sv, hld ' +
            'FROM proj.razz_pitchers'
    )
    df_razz = pd.read_sql_query(query, bbdb)
    df_razz['svhld'] = (df_razz['sv'] + df_razz['hld'])


    query = (
            'SELECT \'fg_dc\' as source, fg_id, ip, qs, era, whip, so, sv, hld ' +
            'FROM proj.fg_dc_pitchers '
    )
    df_fg_dc = pd.read_sql_query(query, bbdb)
    df_fg_dc['qs'] = df_fg_dc['qs'].replace({0: None})
    df_fg_dc['svhld'] = (df_razz['sv'] + df_razz['hld'])
    df = pd.concat([df_razz, df_fg_dc])

    df_ip = df[['source', 'fg_id', 'ip']]    
    
    query_teams = 'SELECT playerid as fg_id, fg_dc_pitchers_raw."Team" as team FROM proj.fg_dc_pitchers_raw'
    df_teams = pd.read_sql_query(query_teams, bbdb)


    # if 'sample' is not predefined then use entire data set
    for var in ls.pitching_counting_stats:
        df[var] = df.apply(lambda row: 0 if pd.isna(row[var]) else row[var], axis=1)



    weights = {'system': ['fg_dc', 'thebat', 'thebatx', 'pod', 'razz'],
               'sys_weight': [1, 1, 1.2, 0, .01]}
    weights = pd.DataFrame(weights)
    df = df.merge(right=weights, how='left', left_on='source', right_on='system')

    weights_ip = {'system': ['fg_dc', 'thebat', 'thebatx', 'pod', 'razz'],
               'sys_weight': [.25, 0, 0, 0, .01]}
    weights_ip = pd.DataFrame(weights_ip)
    df_ip = df_ip.merge(right=weights_ip, how='left', left_on='source', right_on='system')

    def weighted_average(df,data_col,weight_col,by_col):
        df['_data_times_weight'] = df[data_col]*df[weight_col]
        df['_weight_where_notnull'] = df[weight_col]*pd.notnull(df[data_col])
        g = df.groupby(by_col)
        result = g['_data_times_weight'].sum() / g['_weight_where_notnull'].sum()
        del df['_data_times_weight'], df['_weight_where_notnull']
        result = pd.DataFrame(result, columns=[data_col])
        return result


    df.loc[df['source'] == 'fg_dc', 'qs'] = None

    combined_pitchers = pd.DataFrame(df_ip['fg_id'].unique(), columns=['fg_id'])
    statlist = list(set(utilities.flatten([['ip'], ls.pitching_stats])))
    for stat in statlist: # do this list(set(*)) to get unique values b/c ip may be in there twice
        t = weighted_average(df, stat, 'sys_weight', 'fg_id')
        combined_pitchers = combined_pitchers.merge(t, on='fg_id')


    # merge in the names and reorder
    names = player_names.get_player_names()
    combined_pitchers = combined_pitchers.merge(names[['fg_id', 'name']], on='fg_id', how='left')
    combined_pitchers = combined_pitchers.merge(df_teams, on='fg_id', how='left')
    output_stats = ['fg_id', 'name', 'team', 'ip']
    for stat in ls.pitching_stats:
        if (stat in output_stats) is False:
            output_stats.append(stat)
    combined_pitchers = combined_pitchers[output_stats]

    return combined_pitchers


def create_actuals_hitters(ls, year=2021):
    import pandas as pd
    from general import utilities
    from general import postgres
    from general import classes
    from munging import player_names

    bbdb = postgres.connect_to_bbdb()

    if year==2021:
        tablename = 'tracking'
    else:
        tablename = 'reference'

    query = (
        'SELECT year, bbref_id, bat."Tm" as team, bat."PA" as pa, '+
        'bat."HR" as hr, bat."R" as r, bat."RBI" as rbi, bat."SB" as sb, bat."OBP" as obp, bat."OPS" as ops '+
        'FROM '+tablename+'.bbref_batting_standard bat WHERE year='+str(year))
    df = pd.read_sql_query(query, bbdb)
    df = df.fillna(value={'obp':0, 'ops': 0, 'pa':0, 'r':0, 'rbi':0, 'sb':0})
    for c in ['pa', 'r', 'rbi', 'hr', 'sb']:
        df[c] = df[c].replace(r'^\s*$', 0, regex=True)
        df[c] = df[c].astype(int)
    for c in ['obp', 'ops']:
        df[c] = df[c].replace(r'^\s*$', 0, regex=True)
        df[c] = df[c].astype(float)
    df = df[(df['bbref_id'].notnull()) & (df['bbref_id']!=u'')]

    # merge in the names and reorder
    names = player_names.get_player_names()
    combined_hitters = df.merge(names[['bbref_id', 'fg_id', 'name']], on='bbref_id', how='left')
    output_stats = utilities.flatten([['fg_id', 'bbref_id', 'name', 'team', 'pa'],[ls.hitting_stats]])
    combined_hitters = combined_hitters[output_stats]
    combined_hitters.drop_duplicates(inplace=True)
    return combined_hitters

def create_actuals_pitchers(ls, year=2021):
    import pandas as pd
    
    from general import utilities
    from general import postgres
    from munging import player_names

    bbdb = postgres.connect_to_bbdb()
    query = ('SELECT pit_std.year, pit_std.bbref_id, pit_std."Tm" as team, pit_std."IP" as ip, pit_start."GS" as gs, pit_start."QS" as qs, pit_std."SO" as so, pit_std."ERA" as era, pit_std."WHIP" as whip, pit_relief."SV" as sv, pit_relief."Hold" as hld FROM '+
             '(SELECT * FROM tracking.bbref_pitching_standard) as pit_std '+
             'LEFT JOIN (SELECT * FROM tracking.bbref_pitching_starter) as pit_start ON pit_std.bbref_id=pit_start.bbref_id AND pit_std.year=pit_start.year AND pit_std."Tm"=pit_start."Tm" '+
             'LEFT JOIN (SELECT * FROM tracking.bbref_pitching_reliever) as pit_relief ON pit_std.bbref_id=pit_relief.bbref_id AND pit_std.year=pit_relief.year AND pit_std."Tm"=pit_relief."Tm" '+
             'WHERE pit_std.year='+str(year))
    df = pd.read_sql_query(query, bbdb)
    df['ip'] = df['ip'].str.replace('.1', '.33', regex=False)
    df['ip'] = df['ip'].str.replace('.2', '.67', regex=False)
    df = df.fillna(value={'era':0, 'whip': 0, 'gs':0, 'qs':0, 'sv':0, 'hld':0})
    for c in ['gs', 'qs', 'so', 'sv', 'hld']:
        df[c] = df[c].replace(r'^\s*$', 0, regex=True)
        df[c] = df[c].astype(int)
    for c in ['ip', 'era', 'whip']:
        df[c] = df[c].replace(r'^\s*$', 0, regex=True)
        df[c] = df[c].astype(float)
    df['svhld'] = df['sv'] + df['hld']
    df = df[(df['bbref_id'].notnull()) & (df['bbref_id']!=u'')]

    # merge in the names and reorder
    names = player_names.get_player_names()
    combined_pitchers = df.merge(names[['bbref_id', 'fg_id', 'name']], on='bbref_id', how='left')
    output_stats = utilities.flatten([['fg_id', 'name', 'team', 'ip'],[ls.pitching_stats]])
    combined_pitchers = combined_pitchers[output_stats]
    combined_pitchers.drop_duplicates(inplace=True)

    return combined_pitchers



def create_last30_hitters(ls):
    import pandas as pd
    from general import utilities
    from general import postgres
    from general import classes
    from munging import player_names

    bbdb = postgres.connect_to_bbdb()

    query = (
        'SELECT bat.fg_id, bat.team, bat.pa, '+
        'bat.hr, bat.r, bat.rbi, bat.sb, bat.obp, bat.obp+bat.slg as ops '+
        'FROM tracking.batters_last30 AS bat')
    df = pd.read_sql_query(query, bbdb)
    df = df.fillna(value={'obp':0, 'ops': 0, 'pa':0, 'r':0, 'rbi':0, 'sb':0})
    for c in ['pa', 'r', 'rbi', 'hr', 'sb']:
        df[c] = df[c].replace(r'^\s*$', 0, regex=True)
        df[c] = df[c].astype(int)
    for c in ['obp', 'ops']:
        df[c] = df[c].replace(r'^\s*$', 0, regex=True)
        df[c] = df[c].astype(float)
    #df = df[(df['fg_id'].notnull()) & (df['fg_id']!=u'')]

    # merge in the names and reorder
    names = player_names.get_player_names()
    combined_hitters = df.merge(names[['fg_id', 'name']], on='fg_id', how='left')
    output_stats = utilities.flatten([['fg_id', 'name', 'team', 'pa'],[ls.hitting_stats]])
    combined_hitters = combined_hitters[output_stats]
    combined_hitters.drop_duplicates(inplace=True)
    return combined_hitters

