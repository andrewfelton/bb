import sys
sys.path.append('python/general')
import postgres
import pandas as pd
import gspread
import gspread_dataframe

postgres.start_postgres()

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
    gspread_dataframe.set_with_dataframe(bb2021.worksheet(sheettitle), df)
    combined = bb2021.worksheet('Combined')
    combined.update
    print('Updated combined spreadsheet')


def update_inseason_sheet(leagues):




