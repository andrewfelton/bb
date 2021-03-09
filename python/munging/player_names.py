import sys
sys.path.append('python/utilities')
import selenium_utilities
import postgres
import pandas as pd
import os



def get_player_names():
	import sys
	sys.path.append('python/utilities')
	import postgres
	import pandas as pd
	bbdb = postgres.connect_to_bbdb()
	names = pd.read_sql_query(sql='SELECT * FROM REFERENCE.PLAYER_NAMES', con=bbdb)
	for col in ['otto_id']:
		names[col] = names[col].astype('str').replace('\.0', '', regex=True)
	return names


def scrape_sfb_names():
	# Download the latest .csv file from smartfantasybaseball.com

	driver = selenium_utilities.start_driver()
	driver.get("https://www.smartfantasybaseball.com/PLAYERIDMAPCSV")

	filename = '/Users/andrewfelton/Downloads/docker/SFBB Player ID Map - PLAYERIDMAP.csv'
	player_names = pd.read_csv(filename)
	os.remove(filename)

	tablename = 'player_names_sfb'
	bbdb = postgres.connect_to_bbdb()
	command = 'TRUNCATE TABLE reference.' + tablename
	bbdb.execute(command)
	player_names.to_sql(tablename, bbdb, schema='reference', if_exists='append')
	player_names['yahoo_id'] = str(player_names['yahoo_id'])








def get_gs_names():
	import gspread
	import pandas as pd

	#gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')

	sh = gc.open("BB 2021")
	names = sh.worksheet('Names').get_all_values()
	headers = names.pop(0)
	names = pd.DataFrame(names, columns=headers)
	del(headers)
	return names

	import sys
	sys.path.append('python/utilities')
	import postgres
	bbdb = postgres.connect_to_bbdb()

	#names.to_sql('names', bbdb, schema='reference', if_exists='replace')




