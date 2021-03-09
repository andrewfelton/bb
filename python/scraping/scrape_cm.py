def scrape_cm_draft(draft_num, gs=None, db=None):

    import sys
    sys.path.append('python/utilities')
    import postgres
    sys.path.append('python/munging')
    import player_names
    import pandas as pd
    import gspread
    import gspread_dataframe

    #draft_num = '46233' # Testing
    #draft_num = '46117' # SoS Mock
    #draft_num = '46233' # SoS D2
    #draft_num = '46234' # SoS D2
    draft_url = "https://www.couchmanagers.com/mock_drafts/csv/download.php?draftnum="+str(draft_num)

    import requests
    r = requests.get(draft_url).text.splitlines()

    mock = []
    for line in r:
        pick = line.split(',')
        for i in range(0, len(pick)):
            pick[i] = str(pick[i].replace('"', ''))
        mock.append(pick)
    colnames = mock.pop(0)
    mock = pd.DataFrame(mock, columns=colnames)

    names = player_names.get_player_names()

    mock = mock.merge(
        names[['name','fg_id','otto_id']],
        how='left',
        left_on='ottid',
        right_on='otto_id'
    )





    if (gs!=None):
        gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
        bb2021 = gc.open("BB 2021")
        sheettitle = "Mock "+draft_num
        bb2021.values_clear(sheettitle + "!A:Z")
        gspread_dataframe.set_with_dataframe(bb2021.worksheet(sheettitle), mock_long)
        combined = bb2021.worksheet('Combined')
        hitter_projections = bb2021.worksheet('Hitter Projections')
        combined.update
        hitter_projections.update

    if (db!=None):
        bbdb = postgres.connect_to_bbdb()
        mock.to_sql('cm_mock_'+draft_num, bbdb, schema='drafts', if_exists='replace')




#scrape_cm_draft(draft_num='46233', db=True)


