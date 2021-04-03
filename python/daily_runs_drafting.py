import sys
from scraping import scrape_fg_projections
from scraping import scrape_cm
from munging import update_spreadsheets
from analysis import valuations
from analysis import standings

print('Running '+sys.argv[0])

if '-fg' in sys.argv:
    print('Scraping FanGraphs projections...')
    scrape_fg_projections.scrape_all_fg_projections()
    print('Finished scraping FanGraphs')

if '-v' in sys.argv:
    # Update the valuations for each league
    print('Running the valuations...')
    valuations.create_combined_valuations(league='SoS')
    print('Created and uploaded SoS valuations')
    valuations.create_combined_valuations(league='Legacy')
    print('Created and uploaded Legacy valuations')


# Scrape the CM drafts
#print('Scraping SoS draft...')
#scrape_cm.scrape_cm_draft(draft_num='46231', db=True, gs='SoS')
#standings.project_standings('46231')
#print('Updated SoS standings')

print('Scraping Legacy draft')
scrape_cm.scrape_cm_draft(draft_num='46331', db=True, gs='Legacy')
standings.project_standings('46331')
print('Updated Legacy standings')

