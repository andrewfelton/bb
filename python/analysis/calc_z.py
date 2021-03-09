

def calc_z(df, rate_stats, counting_stats, denom, num_teams, players_per_team, budget_split):
    import pandas as pd
    sys.path.append('python/utilities')
    import postgres
    import itertools

    stats = list(itertools.chain(*[counting_stats, rate_stats]))

    for var in counting_stats:
        var_pa = var + '_' + denom
        if (var_pa in df.columns):
            df[var] = df.apply(lambda row: row[var_pa] * row[denom], axis=1)

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

    df['z']=0
    for var in stats:
        df['z'] = df.apply(lambda row: (row['z']+row[var+'_z']), axis=1)

    df['rank'] = df['z'].rank(method='average', ascending=False)

    marginal_z = df[df['rank'] == num_teams*players_per_team]['z'].to_list()[0]
    df['zar'] = df.apply(lambda row: (row['z'] - marginal_z), axis=1)

    sum_zar = df[df['zar']>=0]['zar'].sum()
    df['value'] = df.apply(lambda row: ((num_teams * 260 * budget_split) * row['zar'] / sum_zar), axis=1)

    df = df.sort_values(by='value', ascending=False)

    return_cols = list(itertools.chain(*[['fg_id'], [denom], counting_stats, rate_stats, ['zar', 'value']]))
    df = df[return_cols]
    return df

