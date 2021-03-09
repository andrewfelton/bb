import sys
sys.path.append('python/utilities')
import postgres



# Get the list of names from the FG DC projections
bbdb = postgres.connect_to_bbdb()
query = (
        'SELECT fg_dc_batters.fg_id FROM proj.fg_dc_batters ' +
        'UNION ' +
        'SELECT fg_dc_pitchers.fg_id FROM proj.fg_dc_pitchers'
)
df = pd.read_sql_query(query, bbdb)

df = df.merge(names, how='left', on='fg_id')


test = pd.DataFrame({'fg_id': ['20123', '18032', '17988'], 'otto_id': ['23717', 'nan', None]})



https://ottoneu.fangraphs.com/1275/playercard?id=18263

#https://ottoneu.fangraphs.com/averageValues

otto = pd.read_csv('~/Downloads/ottoneu_average_values.csv')
otto = otto.rename(columns={"Name": "name",
                            "OttoneuID": "otto_id",
                            'FG MajorLeagueID':'fg_id_major',
                            'FG MinorLeagueID':'fg_id_minor',
                            'Position(s)':'position',
                            'ast 10':'last_10',
                            'Roster%':'roster_pct',
                            })

otto['fg_id'] = otto['fg_id_major'].combine_first(otto['fg_id_minor'])
otto['fg_id'] = otto['fg_id'].astype('str').replace('\.0', '', regex=True)

otto.to_sql('player_names_otto', bbdb, schema='reference', if_exists='replace')


#http://www.fangraphs.com/statss.aspx?playerid=10155

