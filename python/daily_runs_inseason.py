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

# Scrape latest data
if '-fg' in sys.argv or '-all' in sys.argv:
    print('Scraping FanGraphs projections...')
    scrape_fg_projections.scrape_all_fg_projections()
    scrape_fg_projections.scrape_fg_leaderboard(fg_leaderboard_url='https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=c%2c7%2c13%2c11%2c114%2c70%2c63%2c-1%2c6%2c224%2c62%2c122%2c332%2c-1%2c331%2c120%2c121%2c113%2c-1%2c139%2c-1%2c43%2c44%2c51&season=2021&month=2&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate=2021-01-01&enddate=2021-12-31&sort=8%2cd&page=1_500')
    update_spreadsheets.update_relievers_last14()
    print('Finished scraping FanGraphs')

if '-bp' in sys.argv or '-all' in sys.argv:
    print('Scraping Baseball Prospectus metrics...')
    scrape_prospectus.scrape_bp_pitching()
    print('Finished scraping BP')

if '-savant' in sys.argv or '-all' in sys.argv:
    print('Scraping Baseball Savant metrics...')
    scrape_savant.scrape_savant()
    print('Finished scraping Savant')

if '-xxxfip' in sys.argv or '-all' in sys.argv:
    print('Scraping xxxFIP metrics...')
    scrape_xxxfip.scrape_xxxfip()
    print('Finished scraping xxxFIP')

if '-bbref' in sys.argv or '-all' in sys.argv:
    print('Scraping Baseball Reference actual data...')
    scrape_bbref.scrape_actuals()
    print('Finished scraping actuals')
    

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
pd.set_option("display.max_columns", 10)
pd.set_option('display.max_colwidth', 120)
pd.set_option('display.precision', 2)
pd.set_option('display.width', 120)

if '-razz' in sys.argv or '-all' in sys.argv:
    razz_streamers = scrape_razzball.scrape_razz(mytype='streamers', url="https://razzball.com/streamers/")

    # print the best upcoming streamers for SoS
    print('Good upcoming streamers for SoS:')
    print(
        razz_streamers[
            (razz_streamers['SoS_Team'].isna()) & (razz_streamers['era']<4.0)
        ].
        append(
            razz_streamers[(razz_streamers['SoS_Team']=='JohnnyFang\'s Team')]
        )[
            ['SoS_Team', 'fg_id', 'name', 'opp', 'date', 'value', 'qs', 'era', 'whip', 'k']
        ].
        sort_values(by=['date', 'era'], ascending=[True, True])
    )

    # print the best Legacy streamers
    print('Best upcoming value streams for Legacy:')
    print(
        razz_streamers[
            (razz_streamers['Legacy_Team'].isna()) & (razz_streamers['era']<4.0)
        ].
        append(
            razz_streamers[(razz_streamers['Legacy_Team']=='Johnny Fang')]
        )[
            ['Legacy_Team', 'fg_id', 'name', 'opp', 'date', 'value', 'ip', 'era', 'whip', 'k']
        ].
        sort_values(by=['date', 'value'], ascending=[True, False])
    )


    razz_streamers = dict()
    for date in ['today','tomorrow', 'day3']:
        razz_streamers[date] = scrape_razzball.scrape_razz(mytype='hittertron-'+date, url="https://razzball.com/hittertron-"+date)
        print('Scraped hittertron for '+date)

    razz_streamers_agg = pd.concat(razz_streamers.values(), ignore_index=True)

    print('\n\nPotential hitting streamers for SoS')
    for date in ['today','tomorrow', 'day3']:
        print('\n' + date + '\n---------------------')
        razz = razz_streamers[date]
        print(
            # Prob of SB > 10%
            razz[
                (razz['SoS_Team'].isna()) & (razz['sb']>.10)
            ].head(5).
            # Top 10 values
            append(
                razz[
                    (razz['SoS_Team'].isna())
                ].sort_values(by=['value'], ascending=[False]).head(10)
            ).
            append(
                razz[(razz['SoS_Team']=='JohnnyFang\'s Team')]
            )[['date', 'SoS_Team', 'fg_id', 'name', 'opp', 'pitcher', 'value', 'sb']].
            sort_values(by=['value'], ascending=[False]).
            drop_duplicates()
        )



    print('\n\nPotential hitting streamers for Legacy')
    for date in ['today','tomorrow', 'day3']:
        print('\n' + date + '\n---------------------')
        razz = razz_streamers[date]
        print(
            razz[
                (razz['Legacy_Team'].isna()) & (razz['sb']>.10)
            ].head(5).
            append(
                razz[
                    (razz['Legacy_Team'].isna())
                ].sort_values(by=['value'], ascending=[False]).head(5)
            ).
            append(
                razz[(razz['Legacy_Team']=='Johnny Fang')]
            )[['date', 'Legacy_Team', 'fg_id', 'name', 'opp', 'pitcher', 'value', 'sb']].
            sort_values(by=['value'], ascending=[False]).
            drop_duplicates()
        )

