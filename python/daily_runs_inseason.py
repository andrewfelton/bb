import sys
from scraping import scrape_fg_projections
from scraping import scrape_ff
from scraping import scrape_razzball
#from munging import update_spreadsheets
from analysis import valuations
from general import classes
from general import utilities

print('Running '+sys.argv[0])
league_sos = classes.league('SoS')
league_legacy = classes.league('Legacy')


# Scrape latest projections
if '-fg' in sys.argv or '-all' in sys.argv:
    print('Scraping FanGraphs projections...')
    scrape_fg_projections.scrape_all_fg_projections()
    print('Finished scraping FanGraphs')

# Update combined projections


# Update eligibilities


# Update valuations


# Update rosters
print('Updating for ' + league_sos.league_name)
rosters_sos = scrape_ff.rosters(league_sos)


# Post updates to Google Sheets
if '-v' in sys.argv or '-all' in sys.argv:
    # Update the valuations for each league
    print('Running the valuations...')
    valuations.update_inseason_valuations(league_sos, league_legacy)
    print('Created and uploaded valuations')


# print upcoming streamers
if '-razz' in sys.argv or '-all' in sys.argv:
    scrape_razzball.scrape_razz(mytype='streamers', url="https://razzball.com/streamers/")



