def create_combined_hitters(ls):
    import sys
    sys.path.append('python/utilities')
    import utilities
    sys.path.append('python/munging')
    import postgres
    import pandas as pd
    import player_names

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
            'UNION ' +
            'SELECT \'pod\' as source, fg_id, pa ' +
            'FROM proj.pod_batters ' +
            ') AS proj'
    )
    df_pa = pd.read_sql_query(query_pa, bbdb)


    query_teams = 'SELECT playerid as fg_id, fg_dc_batters_raw."Team" as team FROM proj.fg_dc_batters_raw'
    df_teams = pd.read_sql_query(query_teams, bbdb)

    weights = {'system': ['fg_dc', 'thebat', 'thebatx', 'pod'],
               'sys_weight': [1, 1, 1.2, 1]}
    weights = pd.DataFrame(weights)
    df = df.merge(right=weights, how='left', left_on='source', right_on='system')
    df_pa = df_pa.merge(right=weights, how='left', left_on='source', right_on='system')

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
    import sys
    sys.path.append('python/utilities')
    import utilities
    sys.path.append('python/munging')
    import postgres
    import pandas as pd
    import player_names

    bbdb = postgres.connect_to_bbdb()
    query = (
            'SELECT proj.* FROM (' +
            'SELECT \'fg_dc\' as source, fg_id, ip, qs, era, whip, so, sv, hld, svhld  ' +
            'FROM proj.fg_dc_pitchers ' +
            'UNION ' +
            'SELECT \'pod\'   as source, fg_id, ip, qs, era, whip, so, sv, hld, svhld  ' +
            'FROM proj.pod_pitchers ' +
            ') AS proj'
    )
    df = pd.read_sql_query(query, bbdb)

    query_ip = (
            'SELECT proj.* FROM (' +
            'SELECT \'fg_dc\' as source, fg_id, ip FROM proj.fg_dc_pitchers ' +
            'UNION ' +
            'SELECT \'pod\' as source, fg_id, ip FROM proj.pod_pitchers ' +
            ') AS proj'
    )
    df_ip = pd.read_sql_query(query_ip, bbdb)

    query_teams = 'SELECT playerid as fg_id, fg_dc_pitchers_raw."Team" as team FROM proj.fg_dc_pitchers_raw'
    df_teams = pd.read_sql_query(query_teams, bbdb)


    # if 'sample' is not predefined then use entire data set
    for var in ls.pitching_counting_stats:
        df[var] = df.apply(lambda row: 0 if pd.isna(row[var]) else row[var], axis=1)



    weights = {'system': ['fg_dc', 'thebat', 'thebatx', 'pod'],
               'sys_weight': [1, 1, 1.2, 1]}
    weights = pd.DataFrame(weights)
    df = df.merge(right=weights, how='left', left_on='source', right_on='system')
    df_ip = df_ip.merge(right=weights, how='left', left_on='source', right_on='system')

    def weighted_average(df,data_col,weight_col,by_col):
        df['_data_times_weight'] = df[data_col]*df[weight_col]
        df['_weight_where_notnull'] = df[weight_col]*pd.notnull(df[data_col])
        g = df.groupby(by_col)
        result = g['_data_times_weight'].sum() / g['_weight_where_notnull'].sum()
        del df['_data_times_weight'], df['_weight_where_notnull']
        result = pd.DataFrame(result, columns=[data_col])
        return result



    combined_pitchers = pd.DataFrame(df_ip['fg_id'].unique(), columns=['fg_id'])
    for stat in list(set(utilities.flatten([['ip'], ls.pitching_stats]))): # do this list(set(*)) to get unique values b/c ip may be in there twice
        t = weighted_average(df, stat, 'sys_weight', 'fg_id')
        combined_pitchers = combined_pitchers.merge(t, on='fg_id')


    # merge in the names and reorder
    names = player_names.get_player_names()
    combined_pitchers = combined_pitchers.merge(names[['fg_id', 'name']], on='fg_id', how='left')
    combined_pitchers = combined_pitchers.merge(df_teams, on='fg_id', how='left')
    output_stats = utilities.flatten([['fg_id', 'name', 'team', 'ip'],[ls.pitching_stats]])
    combined_pitchers = combined_pitchers[output_stats]

    return combined_pitchers

