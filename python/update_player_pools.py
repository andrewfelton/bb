import sys
from scraping import scrape_fg_projections
from scraping import scrape_ff
from scraping import scrape_razzball
from scraping import scrape_prospectus
from scraping import scrape_yahoo
from scraping import scrape_savant
from scraping import scrape_xxxfip
from scraping import scrape_bbref
from munging import update_spreadsheets
from analysis import valuations
from general import classes
from general import utilities
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.precision', 2)

print('Running '+sys.argv[0])
league_sos = classes.league('SoS')
league_legacy = classes.league('Legacy')

if '-yahoo' in sys.argv or len(sys.argv)==0:
    print('\nScraping Yahoo player pool...')
    scrape_yahoo.scrape_yahoo_player_pool()
    print('Finished scraping Yahoo player pool\n')

if '-ff' in sys.argv or '-fleaflicker' in sys.argv or len(sys.argv)==0:
    print('\nScraping Fleaflicker player pool...')
    scrape_ff.scrape_ff_player_pool()
    print('Finished scraping Fleaflicker player pool\n')
