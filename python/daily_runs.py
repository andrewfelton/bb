from scraping import scrape_fg_projections
from scraping import scrape_cm
from utilities import postgres
postgres.start_postgres()

print('Scraping FanGraphs projections')
scrape_fg_projections.scrape_all_fg_projections()

scrape_cm.scrape_cm_draft(draft_num='46233', db=True)
scrape_cm.scrape_cm_draft(draft_num='46234', db=True)



