import sys
sys.path.append('python/utilities')
import postgres
sys.path.append('python/munging')
import player_names
sys.path.append('python/analysis')
import league_settings
import pandas as pd
import gspread
import gspread_dataframe

ls = league_settings('SoS')
bbdb = postgres.

query = (
        'SELECT fg_dc_batters.fg_id, player_names.name, pa, hr_pa, r_pa, rbi_pa, sb_pa, obp, ops ' +
        'FROM proj.fg_dc_batters ' +
        'LEFT JOIN reference.player_names ON fg_dc_batters.fg_id=player_names.fg_id'
)
df = pd.read_sql_query(query, bbdb)

df['sample'] = df.apply(lambda row: row.pa > 500, axis=1)
df = calc_z(df,
            rate_stats=hitting_rate_stats, counting_stats=hitting_counting_stats, denom='pa',
            num_teams=num_teams, players_per_team=hitters_per_team,
            budget_split=batting_split)



viable = df[df['value']>-20]
viable = viable.merge(names, how='left', on='fg_id')
viable.to_csv('~/Downlaods/viable.csv')







