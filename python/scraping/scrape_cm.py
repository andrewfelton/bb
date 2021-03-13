def scrape_cm_draft(draft_num, gs=None, db=None):

    import sys
    sys.path.append('python/utilities')
    import postgres
    sys.path.append('python/munging')
    import player_names
    import pandas as pd
    import gspread
    import gspread_dataframe
    import requests

    #draft_num = '46233' # SoS D2 testing
    draft_url = "https://www.couchmanagers.com/mock_drafts/csv/download.php?draftnum="+str(draft_num)
    print('Going to scrape draft '+draft_num+' from '+draft_url)
    r = requests.get(draft_url).text.splitlines()
    print('Downloaded the .csv')

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
    mock = mock[['Pick','Rd','Owner','name','fg_id']]
    print('Munged into mock draft format')

    if (gs!=None):
        gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
        bb2021 = gc.open("BB 2021 SoS")
        sheettitle = "Mock "+draft_num
        if (sheettitle in bb2021.worksheets() == False):
            bb2021.add_worksheet(title=sheettitle, rows='1', cols='1')
        else:
            bb2021.values_clear(sheettitle + "!A:Z")
        gspread_dataframe.set_with_dataframe(bb2021.worksheet(sheettitle), mock)
        combined = bb2021.worksheet('Combined')
        hitter_projections = bb2021.worksheet('Hitter Projections')
        combined.update
        hitter_projections.update
        print('Updated Google sheet')

    if (db!=None):
        print('Trying to connect to database')
        bbdb = postgres.connect_to_bbdb()
        print('Connected to database')
        mock.to_sql('cm_mock_'+draft_num, bbdb, schema='drafts', if_exists='replace')
        print('Updated database')




#scrape_cm_draft(draft_num='46233', db=True)


