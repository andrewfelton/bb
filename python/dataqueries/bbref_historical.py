# This scrapes historical data from bbref and uploads into bbdb

from python.munging import import_bbref
from python.utilities import postgres
from python.scraping import scrape_bbref

postgres.connect_to_bbdb()

# Get player position eligibility
urlprefix = 'https://www.baseball-reference.com/leagues/MLB/'
urlsuffix = '-appearances-fielding.shtml'
tableid = 'players_players_appearances_fielding'
year = 2020


positions = scrape_bbref.scrape_bbref(urlprefix, year, urlsuffix, tableid)




bbref_qs = import_bbref.import_bbref('~/Documents/bb/2021/data/bbref_qs_historical.csv')
bbref_qs = bbref_qs.rename(columns={"W-L%": "W-Lpct", "K%": "Kpct", "BB%" : "BBpct"})

bbref_qs.to_sql('bbref_qs', con=engine, if_exists='replace')

