# This just has useful stuff to run while coding

from datetime import date
from datetime import datetime
import time

import sys
sys.path.append('python/general')
import utilities
import postgres
import classes
sys.path.append('python/munging')
import player_names
sys.path.append('python/analysis')
import valuations
import calculations
import create_combined
sys.path.append('python/scraping')

import pandas as pd
import gspread
import gspread_dataframe as gsdf

league_sos = classes.league('SoS')
league_legacy = classes.league('Legacy')
ls = league_sos
league = league_sos

pd.set_option('display.max_columns', None)
pd.set_option('display.precision', 2)
pd.set_option('display.min_rows', 5)
