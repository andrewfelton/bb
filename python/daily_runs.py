from scraping import scrape_fg_projections
from scraping import scrape_cm
from utilities import postgres
import pandas as pd
import gspread
import gspread_dataframe
postgres.start_postgres()

print('Scraping FanGraphs projections')
scrape_fg_projections.scrape_all_fg_projections()

scrape_cm.scrape_cm_draft(draft_num='46233', db=True)
print('Scraped CM draft 46233')
scrape_cm.scrape_cm_draft(draft_num='46234', db=True)
print('Scraped CM draft 46234')

bbdb = postgres.connect_to_bbdb()
query = (
'SELECT fg_id, MIN(draft."Pick"::DOUBLE PRECISION) as min_pick, AVG(draft."Pick"::DOUBLE PRECISION) as avg_pick '+
'FROM ( '+
'	SELECT fg_id, cm_mock_46233."Pick" '+
'	FROM drafts.cm_mock_46233 '+
'	UNION ' +
'	SELECT fg_id, cm_mock_46234."Pick" '+
'	FROM drafts.cm_mock_46234) AS draft '+
'GROUP BY fg_id'
)
df = pd.read_sql_query(query, bbdb)
gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
bb2021 = gc.open("BB 2021 SoS")
sheettitle = "D2 drafts"
bb2021.values_clear(sheettitle + "!A:Z")
gspread_dataframe.set_with_dataframe(bb2021.worksheet(sheettitle), df)
combined = bb2021.worksheet('Combined')
combined.update



