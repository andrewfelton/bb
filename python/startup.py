# This just has useful stuff to run while coding

print('Running startup.py')

from datetime import date
from datetime import datetime
import time
import pandas as pd
import gspread
import gspread_dataframe as gsdf


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
from general import postgres

league_sos = classes.league('SoS')
league_legacy = classes.league('Legacy')
ls = league_sos
league = league_sos

pd.set_option('display.max_columns', None)
pd.set_option('display.precision', 2)
pd.set_option('display.min_rows', 5)
