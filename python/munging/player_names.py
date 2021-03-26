import sys
sys.path.append('python/utilities')
import selenium_utilities
import postgres
import pandas as pd
import os
import gspread
import pandas as pd
import gspread_dataframe as gsdf


def get_player_names():
	import sys
	sys.path.append('python/utilities')
	import postgres
	import pandas as pd
	bbdb = postgres.connect_to_bbdb()
	names = pd.read_sql_query(sql='SELECT * FROM REFERENCE.PLAYER_NAMES', con=bbdb)
	for col in ['otto_id', 'yahoo_id', 'bp_id', 'espn_id']:
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

	sh = gc.open("BB 2021 Name Matching")
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


def post_names_to_gs():
	import gspread
	import pandas as pd
	import gspread_dataframe as gsdf

	names = player_names.get_player_names()
	gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
	sh = gc.open("BB 2021 Name Matching")
	gsdf.set_with_dataframe(sh.worksheet('DB Names'), names)


def put_missing_in_GS(id_list, type):
	names = player_names.get_player_names()
	missing = []
	missing = id_list[id_list[type].isin(names[type])==False][[type]]

	if (len(missing)>0):
		gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
		sh = gc.open("BB 2021 Name Matching").worksheet('Override')
		gsdf.set_with_dataframe(sh, missing)
		print('Put '+str(len(missing))+' '+str(type)+' ids in the Google Sheet!')
		print(str(sh.spreadsheet.url)+'/edit#gid='+str(sh.id))
	else:
		print('No missing ids')




def import_GS_into_names_db():
	import gspread
	import pandas as pd
	bbdb = postgres.connect_to_bbdb()
	names_manual = pd.read_sql_query(sql='SELECT * FROM reference.player_names_manual', con=bbdb)

	gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
	sh = gc.open("BB 2021 Name Matching").worksheet('DB Import')
	manual_updates = gsdf.get_as_dataframe(sh)
	manual_updates = manual_updates.dropna(axis=0, how='all')

	to_drop = []
	for col in manual_updates.columns:
		if 'Unnamed: ' in col:
			to_drop = to_drop.append(col)
	if len(to_drop)>0:
		manual_updates.drop(columns = to_drop)
	manual_updates = manual_updates[['fg_id'] + [col for col in manual_updates.columns if col != 'fg_id']]

	# convert any numeric ids into text
	for col in ['fg_id', 'otto_id', 'yahoo_id', 'bp_id', 'espn_id']:
		if col in manual_updates.columns:
			manual_updates[col] = manual_updates[col].astype('str').replace('\.0', '', regex=True)




	sql = 'INSERT INTO reference.player_names_manual (fg_id) VALUES '
	insert_rows = []
	for row in manual_updates['fg_id']:
		row_string = '(\'' + row + '\')'
		insert_rows.append(row_string)
	sql = sql + ','.join(insert_rows) + ';'
	bbdb.execute(sql)


	def create_sql(row, cols):
		sql = 'UPDATE reference.player_names_manual SET '
		updates = []
		for col in cols:
			if col not in ['fg_id', 'sql'] and pd.isna(row[col]) is False and str(row[col])!='nan':
				update_str = str(col) + ' = \'' + str(row[col]) + '\''
				updates.append(update_str)
		sql = sql + ','.join(updates)
		sql = sql + ' WHERE fg_id = \'' + str(row['fg_id']) + '\''
		print(sql)
		return sql

	manual_updates['sql'] = manual_updates.apply(lambda row: create_sql(row, manual_updates.columns), axis=1)

	for update in manual_updates['sql'].tolist():
		bbdb.execute(update)



#import_GS_into_names_db()
