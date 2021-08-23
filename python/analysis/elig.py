def get_eligibilities(league):
    import sys
    sys.path.append('python/general')
    from general import postgres
    import pandas as pd

    bbdb = postgres.connect_to_bbdb()
    query = (
            'SELECT fg_id, elig '
            'FROM reference.player_pool_ff '
    )
    df = pd.read_sql_query(query, bbdb)
    return df

def update_eligibilities(df, league):
    import gspread
    import gspread_dataframe as gsdf

    gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
    bb2021 = gc.open("BB 2021 " + league)
    gs_eligibility = bb2021.worksheet('eligibility')
    gsdf.set_with_dataframe(gs_eligibility, df[['fg_id','Name','elig']])



#eligibilities = get_eligibilities('SoS')
#update_eligibilities(df=eligibilities, league='SoS')
