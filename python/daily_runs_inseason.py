import sys
from scraping import scrape_fg_projections
from scraping import scrape_ff
from scraping import scrape_razzball
from scraping import scrape_prospectus
from scraping import scrape_yahoo
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

# Scrape latest projections
if '-fg' in sys.argv or '-all' in sys.argv:
    print('Scraping FanGraphs projections...')
    scrape_fg_projections.scrape_all_fg_projections()
    print('Finished scraping FanGraphs')

if '-bp' in sys.argv or '-all' in sys.argv:
    print('Scraping Baseball Prospectus metrics...')
    scrape_prospectus.scrape_bp_pitching()
    print('Finished scraping BP')



# Update combined projections


# Update eligibilities


# Update valuations


# Update rosters
print('Updating for ' + league_sos.league_name)
rosters_sos = scrape_ff.rosters(league_sos)

print('Updating for ' + league_legacy.league_name)
rosters_legacy = scrape_yahoo.scrape_yahoo_roster(league_num='26574')

# Post updates to Google Sheets
if '-v' in sys.argv or '-all' in sys.argv:
    # Update the valuations for each league
    print('Running the valuations...')
    valuations.update_inseason_valuations(league_sos, league_legacy)
    print('Created and uploaded valuations')

    scrape_ff.scrape_standings(league_sos)
    update_spreadsheets.inseason_standings_sos()
    print('Updated the standings')


# print upcoming streamers
if '-razz' in sys.argv or '-all' in sys.argv:
    razz_streamers = scrape_razzball.scrape_razz(mytype='streamers', url="https://razzball.com/streamers/")

    # print the best streamers
    best_streamers = razz_streamers[razz_streamers['Team'].isna()].sort_values(by='qs', ascending=False)
    best_streamers = best_streamers[['fg_id', 'name', 'opp', 'date', 'value', 'qs', 'era']]
    print('Five best upcoming prob of QS:')
    print(best_streamers.head(5))

    for date in ['today','tomorrow']:
        razz_streamers = scrape_razzball.scrape_razz(mytype='hittertron-'+date, url="https://razzball.com/hittertron-"+date)
        available_hitters = razz_streamers[razz_streamers['Team'].isna()].sort_values(by='value', ascending=False)
        my_hitters = razz_streamers[razz_streamers['Team']=='JohnnyFang\'s Team']

        # print the best streamers
        print(date + '\'s five most valuable hitters:')
        best_hitters = available_hitters.head(5).append(my_hitters).sort_values(by='value', ascending=False)
        print(best_hitters[['fg_id', 'name', 'opp', 'pitcher', 'value']])

        print(date + '\'s five most likely to SB:')
        best_hitters = razz_streamers[razz_streamers['Team'].isna()].sort_values(by='sb', ascending=False)
        print(best_hitters[['fg_id', 'name', 'opp', 'value', 'sb']].head(5))
