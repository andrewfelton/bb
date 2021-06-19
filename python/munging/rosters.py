

def import_league_rosters(csv_path):
    # csv_path = '/Users/andrewfelton/Documents/bb/2021/data/rosters/rosters_23172_2021-03-28.csv'
    import pandas as pd
    rosters = pd.read_csv(csv_path)
    rosters['ff_id'] = rosters['ff_id'].apply(str)
    return rosters


def get_ff_ownership():
    import pandas as pd
    import sys
    sys.path.append('python/general')
    import postgres

    bbdb = postgres.connect_to_bbdb()
    ff_ownership = pd.read_sql('SELECT * FROM rosters.sos', bbdb)
    return ff_ownership


def get_legacy_ownership():
    import pandas as pd
    import sys
    sys.path.append('python/general')
    import postgres

    bbdb = postgres.connect_to_bbdb()
    ff_ownership = pd.read_sql('SELECT * FROM rosters.legacy', bbdb)
    return ff_ownership


