def get_eligibilities(league):
    import sys
    sys.path.append('python/utilities')
    import postgres
    import pandas as pd

    bbdb = postgres.connect_to_bbdb()
    query = (
            'SELECT pos_elig_sos.* '
            'FROM reference.pos_elig_sos '+
            'WHERE pos_elig_sos.YEAR=2020'
    )
    df = pd.read_sql_query(query, bbdb)

    def combine_eligibilities(row):
        eligibilities = []
        for pos in ['c', '1b', '2b', 'ss', '3b', 'of']:
            if row['elig_' + pos] == True:
                eligibilities.append(pos)
        elig = ' '.join(eligibilities).strip()
        if elig=='':
            elig='ut'
        return elig

    df['elig'] = df.apply(lambda row: combine_eligibilities(row), axis=1)

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
