def calc_z(df, ls, type):
    import sys
    sys.path.append('python/utilities')
    import utilities
    sys.path.append('python/analysis')
    import elig

    assert type in ['hitting', 'batting', 'pitching']
    if (type=='batting' or type=='hitting'):
        counting_stats = ls.hitting_counting_stats
        rate_stats = ls.hitting_rate_stats
        players_per_team = ls.hitters_per_team
        budget_split = ls.batting_split
        denom = 'pa'
    if (type=='pitching'):
        counting_stats = ls.pitching_counting_stats
        rate_stats = ls.pitching_rate_stats
        players_per_team = ls.pitchers_per_team
        budget_split = 1-ls.batting_split
        denom = 'ip'

    stats = utilities.flatten([counting_stats, rate_stats])

    # if 'sample' is not predefined then use entire data set
    if (('sample' in df.columns)==False):
        df['sample'] = True

    # calculate mean and standard deviation
    mean = df[df['sample']==True].mean()
    sd = df[df['sample']==True].std()


    for var in stats:
        var_z = var + '_z'
        df[var_z] = df.apply(lambda row: (row[var] - mean[var])/sd[var], axis=1)
        if (var in rate_stats):
            df[var_z] = df.apply(lambda row: row[var_z]*row[denom]/mean[denom], axis=1)
            if (type == 'pitching'):
                df[var_z] = -df[var_z]
        df[var_z] = ls.z_weights[var] * df[var_z]

    df['z']=0
    for var in stats:
        df['z'] = df.apply(lambda row: (row['z']+row[var+'_z']), axis=1)

    df['rank'] = df['z'].rank(method='average', ascending=False)

    marginal_z = df[df['rank'] == ls.num_teams*players_per_team]['z'].to_list()[0]
    df['zar'] = df.apply(lambda row: (row['z'] - marginal_z), axis=1)

    # Catcher adjustment
    if (type=='batting' or type=='hitting'):
        if not('elig' in df.columns):
            eligibilities = elig.get_eligibilities('SoS')
            df = df.merge(eligibilities[['fg_id','elig']], on='fg_id', how='left')
        df['catcher'] = df.apply(lambda row: 'c' in str(row['elig']), axis=1)
        catchers = df[df['catcher']]
        catchers['rank'] = catchers['zar'].rank(ascending=False)
        catcher_repl = catchers.iloc[16]['zar']
        def add_catcher_repl(row):
            if row['catcher']:
                return row['zar'] - catcher_repl
            else:
                return row['zar']
        df['zar'] = df.apply(lambda row: add_catcher_repl(row), axis=1)
        del(df['catcher'])

    if (type=='pitching'):
        df['zar_skills'] = df['era_z']+df['whip_z']+df['so_z']
        df['elig'] = df.apply(lambda row: 'sp' if (row['qs']>0) else 'rp', axis=1)
        df['rank_sp'] = df[df['elig']=='sp']['zar'].rank(ascending=False)
        df['rank_rp'] = df[df['elig']=='rp'].groupby('team')['zar'].rank(ascending=False)


    sum_zar = df[df['zar']>=0]['zar'].sum()
    df['value'] = df.apply(lambda row: ((ls.num_teams * 260 * budget_split) * row['zar'] / sum_zar), axis=1)

    df = df.sort_values(by='value', ascending=False)

    #return_cols = utilities.flatten([['fg_id'], [denom], counting_stats, rate_stats, ['zar', 'value']])
    #df = df[return_cols]
    return df

