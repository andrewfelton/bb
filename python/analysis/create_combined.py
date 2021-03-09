sys.path.append('python/utilities')
import postgres
from python.analysis import calc_z
import pandas as pd



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

combined = pd.DataFrame(df['fg_id'].unique(), columns=['fg_id'])


weights = {'system': ['fg_dc', 'thebat', 'thebatx', 'pod'],
           'sys_weight': [1, 1, 1.2, 1]}
weights = pd.DataFrame(weights)
df = df.merge(right=weights, how='left', left_on='source', right_on='system')

def weighted_average(df,data_col,weight_col,by_col):
    df['_data_times_weight'] = df[data_col]*df[weight_col]
    df['_weight_where_notnull'] = df[weight_col]*pd.notnull(df[data_col])
    g = df.groupby(by_col)
    result = g['_data_times_weight'].sum() / g['_weight_where_notnull'].sum()
    del df['_data_times_weight'], df['_weight_where_notnull']
    result = pd.DataFrame(result, columns=[data_col])
    return result

t = weighted_average(df, 'hr_pa', 'sys_weight', 'fg_id')

combined = combined.merge(t, on='fg_id')







if (1==0):


