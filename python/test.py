import sys
sys.path.append('python')
import startup
sys.path.append('python/general')
import utilities
import postgres
import classes
sys.path.append('python/munging')
import player_names
import rosters
sys.path.append('python/analysis')
import valuations
import calculations
import player_pool_stats
sys.path.append('python/scraping')
import scrape_razzball
import scrape_bbref

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


actuals_hitters = player_pool_stats.create_actuals_hitters(ls=league_sos, year=2021)
act_hit_values = valuations.create_hitter_valuations(league=league_sos, stats=actuals_hitters)


#with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #print(hitters[['fg_id', 'name', 'pa', 'hr', 'rbi', 'zar']].head(100))

    #print(hitters[hitters['elig']=='C'][['fg_id', 'name', 'pa', 'zar']].head(30))

#print(hitters.loc[589])
#print(actuals_hitters.loc[100])
