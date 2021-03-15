from scraping import scrape_fg_projections
from scraping import scrape_cm
from munging import update_spreadsheets
from analysis import create_full_valuations
from analysis import standings

print('Scraping FanGraphs projections')
#scrape_fg_projections.scrape_all_fg_projections()
print('Finished scraping FanGraphs')

# Update the valuations for each league
create_full_valuations.create_combined_valuations(league='SoS')
#create_full_valuations.create_combined_valuations(league='Legacy')
print('Created and uploaded the valuations')


# Scrape the CM drafts
print('Scraping SoS draft')
scrape_cm.scrape_cm_draft(draft_num='46231', db=True, gs=True)
standings.project_standings('46231')
print('Updated SoS standings')

print('Scraping D2 drafts')
d2_drafts = ['46233', '46234']
for draftnum in d2_drafts:
    scrape_cm.scrape_cm_draft(draft_num=draftnum, db=True)
    print('Scraped CM draft '+draftnum)
update_spreadsheets.post_sos_d2_drafts(d2_drafts)
print('Done with daily run')
