def import_bbref(filename):
    # filename = 'data/bbref_qs_historical.csv'
    import pandas as pd

    df = pd.read_csv(filename)

    del(df['Rk'])

    if ('Player' in df.columns):
        df['Name'] = df['Player']
        del(df['Player'])

    df[['name','bbref_id']] = df['Name'].str.split('\\', expand=True)
    df[['name']] = df['name'].str.replace('\*','', regex=True)
    df[['name']] = df['name'].str.replace('\#','', regex=True)
    del(df['Name'])

    # Filter to only have annual totals
    df[['has_tot']] = df['Tm']=='TOT'
    df[['has_tot']] = df.groupby('bbref_id')['has_tot'].transform('max')
    df = df.drop(df[(df['has_tot']==1) & (df['Tm']!='TOT')].index)
    del(df['has_tot'])

    if ('Lg' in df.columns):
        df[['tot_mlb']] = (df['Tm']=='TOT') & (df['Lg']=='MLB')
        df[['tot_mlb']] = df.groupby('bbref_id')['tot_mlb'].transform('max')
        df = df.drop(df[(df['tot_mlb']==1) & (df['Lg']!='MLB')].index)
        del(df['tot_mlb'])


    colnames = df.columns.tolist()
    colnames.remove('name')
    colnames.insert(0, 'name')
    colnames.remove('bbref_id')
    colnames.insert(1, 'bbref_id')

    df = df.reindex(columns=colnames)
    return df


#bbref_batters = import_bbref('data/bbref_batters_2020.csv')
#bbref_pitchers = import_bbref('data/bbref_pitchers_2020.csv')
#bbref_fielding_2020 = import_bbref('data/bbref_fielding_appearances_2020.csv')
#bbref_qs = import_bbref('data/bbref_qs_historical.csv')

