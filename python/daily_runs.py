from scraping import scrape_fg_projections
from scraping import scrape_cm
from munging import update_spreadsheets

print('Scraping FanGraphs projections')
#scrape_fg_projections.scrape_all_fg_projections()
print('Finished scraping FanGraphs')

# Update the valuations for each league




# Scrape the CM drafts
print('Scraping CM drafts')
d2_drafts = ['46233', '46234']
for draftnum in d2_drafts:
    scrape_cm.scrape_cm_draft(draft_num=draftnum, db=True)
    print('Scraped CM draft '+draftnum)
update_spreadsheets.post_sos_d2_drafts(d2_drafts)

