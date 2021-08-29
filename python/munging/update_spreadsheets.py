import pandas as pd
import gspread
import gspread_dataframe as gsdf

from general import postgres

def post_sos_d2_drafts(draftnums):

    # Calc avg. and min. values for D2 draft
    bbdb = postgres.connect_to_bbdb()
    query = 'SELECT fg_id, MIN(draft."Pick"::DOUBLE PRECISION) as min_pick, AVG(draft."Pick"::DOUBLE PRECISION) as avg_pick FROM ('
    select_queries = []
    for draftnum in draftnums:
        select_queries.append('SELECT fg_id, cm_mock_'+draftnum+'."Pick" FROM drafts.cm_mock_'+draftnum)
    query = query + ' UNION '.join(select_queries) + ') AS draft GROUP BY fg_id'

    df = pd.read_sql_query(query, bbdb)
    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    bb2021 = gc.open("BB 2021 SoS")
    sheettitle = "D2 drafts"
    bb2021.values_clear(sheettitle + "!A:Z")
    gsdf.set_with_dataframe(bb2021.worksheet(sheettitle), df)
    combined = bb2021.worksheet('Combined')
    combined.update
    print('Updated combined spreadsheet')


def inseason_standings_sos():
    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    bb2021 = gc.open("BB 2021 InSeason")
    bbdb = postgres.connect_to_bbdb()

    # Update standings
    ff_standings = pd.read_sql_query('SELECT * FROM tracking.standings_sos', con=bbdb, parse_dates=['date'])
    sheettitle = "Standings"
    bb2021.values_clear(sheettitle + "!A:Z")
    gsdf.set_with_dataframe(bb2021.worksheet(sheettitle), ff_standings)



def update_relievers_last14():
    bbdb = postgres.connect_to_bbdb()
    relievers_last14 = pd.read_sql('''
        SELECT 
            r."Name", r."Team", ff_elig.ff_elig, r."G", r."IP", r."SV",
            r."HLD", r."gmLI", r."WPA", r."ERA", r."kwERA", 
            r."xFIP", r."SIERA", r."xERA", r."CSW_pct", r."K_pct", 
            r."BB_pct", r."SwStr_pct", r."vFA", r."BABIP", r."LOB_pct", 
            r."HR_FB", r.asof_date, r.fg_id,
            rosters_sos."Team" as sos_team
        FROM tracking.relievers_last14_raw r
        LEFT JOIN reference.player_pool_ff ff_elig ON r.fg_id=ff_elig.fg_id
        LEFT JOIN rosters.sos rosters_sos ON r.fg_id=rosters_sos.fg_id
        ORDER BY r."WPA" DESC
        ''', con=bbdb)
    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    bb2021 = gc.open("BB 2021 InSeason")
    sheettitle = "Relievers - Last 14"
    bb2021.values_clear(sheettitle + "!A:Z")
    gsdf.set_with_dataframe(bb2021.worksheet(sheettitle), relievers_last14)

    





