import pandas as pd
from python.utilities import postgres
bbdb = postgres.connect_to_bbdb()
names = pd.read_sql_query('SELECT * FROM reference.player_names', con=bbdb)

#name = 'fg_dc_batters'
def import_fg_hitters(name):
    filename = './data/'+name+'.csv'
    df = pd.read_csv(filename)
    df = df.rename(columns={'playerid':'fg_id'})

    vars = ['fg_id', 'Team', 'G', 'PA', 'AB', 'TB', 'TOB', 'H', 'AVG', 'OBP', 'SLG', 'HR', 'RBI', 'R', 'SB']
    df = df.reindex(vars, axis=1)
    df['TB'] = df['SLG']*df['AB']
    df['TOB'] = df['OBP']*df['PA']
    df['H'] = df['AVG']*df['AB']
    df = df.merge(names[['fg_id', 'Canonical']], how='left', on='fg_id')
    vars.insert(1, 'Canonical')
    df = df.reindex(vars, axis=1)
    df.to_sql(name, con=engine, schema='proj', if_exists='replace')
    return df


def import_fg_pitchers(name):
    filename = './data/'+name+'.csv'
    df = pd.read_csv(filename)
    df = df.rename(columns={'playerid': 'fg_id'})
    vars = ['fg_id', 'Team', 'G', 'GS', 'IP', 'W', 'L', 'SV', 'HLD', 'SVHLD', 'ERA', 'H',
            'ER', 'HR', 'SO', 'BB', 'WHIP', 'K/9', 'BB/9', 'FIP']
    df = df.reindex(vars, axis=1)
    df['SVHLD'] = df['SV'] + df['HLD']
    df = df.merge(names[['fg_id', 'Canonical']], how='left', on='fg_id')
    vars.insert(1, 'Canonical')
    df = df.reindex(vars, axis=1)
    df.to_sql(name, con=engine, schema='proj', if_exists='replace')


fg_dc_batters = import_fg_hitters('fg_dc_batters')
fg_dc_pitchers = import_fg_pitchers('fg_dc_pitchers')

thebat_batters = import_fg_hitters('thebat_batters')
thebat_pitchers = import_fg_pitchers('thebat_pitchers')
thebatx_batters = import_fg_hitters('thebatx_batters')
