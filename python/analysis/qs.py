import sys
sys.path.append('/Users/andrewfelton/Documents/bb/2021/python')
from python.munging import import_bbref
from python.utilities import postgres

postgres.connect_to_bbdb()

bbref_qs = import_bbref.import_bbref('~/Documents/bb/2021/data/bbref_qs_historical.csv')
bbref_qs = bbref_qs.rename(columns={"W-L%": "W-Lpct", "K%": "Kpct", "BB%" : "BBpct"})

bbref_qs.to_sql('bbref_qs', con=engine, if_exists='replace')

