def get_player_names():
	import sys
	sys.path.append('python/general')
	import postgres
	import pandas as pd
	bbdb = postgres.connect_to_bbdb()
	names = pd.read_sql_query(sql='SELECT * FROM REFERENCE.PLAYER_NAMES', con=bbdb)
	for col in ['otto_id', 'yahoo_id', 'bp_id', 'espn_id', 'ff_id', 'fg_id']:
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

def put_missing_in_GS(id_list, type):
	names = player_names.get_player_names()
	missing = []
	missing = id_list[id_list[type].isin(names[type])==False][[type]]

	if (len(missing)>0):
		gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
		sh = gc.open("BB 2021 Name Matching").worksheet('Missing from DB')
		gsdf.set_with_dataframe(sh, missing)
		print('Put '+str(len(missing))+' '+str(type)+' ids in the Google Sheet!')
		print(str(sh.spreadsheet.url)+'/edit#gid='+str(sh.id))
	else:
		print('No missing ids')

# deprecated
def import_GS_into_names_db():
	# This imports the "DB Import" Google Sheet and updates the reference.player_names_manual table.
	# If the player wasn't there, it adds him.  If he was there already, it updates the data.
	# It uses fg_id as primary key

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
	for col in ['fg_id', 'otto_id', 'yahoo_id', 'bp_id', 'espn_id', 'ff_id']:
		if col in manual_updates.columns:
			manual_updates[col] = manual_updates[col].astype('str').replace('\.0', '', regex=True)

	sql = 'INSERT INTO reference.player_names_manual (fg_id) VALUES '
	insert_rows = []
	for row in manual_updates['fg_id']:
		row_string = '(\'' + row + '\')'
		insert_rows.append(row_string)
	sql = sql + ','.join(insert_rows) + ';'
	try:
		#bbdb.execute(sql)
		1==1
	except ZeroDivisionError:
		print("divide by zero")

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


def scrape_ff_names():
	# This loops through the FF player pages and saves the player name, id, and eligibility to the database
	from bs4 import BeautifulSoup
	import pandas as pd
	import requests
	import time
	import unidecode

	# pitchers
	# 'https://www.fleaflicker.com/mlb/leagues/23172/players?season=2021&statType=1&sortMode=1&isFreeAgent=false&position=1536&tableSortName=pv7&tableSortDirection=DESC'
	# 'https://www.fleaflicker.com/mlb/leagues/23172/players?season=2021&statType=1&sortMode=1&position=1536&isFreeAgent=false&tableSortDirection=DESC&tableSortName=pv7&tableOffset=20'

	pitcher_base_url = 'https://www.fleaflicker.com/mlb/leagues/23172/players?season=2021&statType=1&sortMode=1&position=1536&isFreeAgent=false&tableSortDirection=DESC&tableSortName=pv7&tableOffset='
	hitter_base_url  = 'https://www.fleaflicker.com/mlb/leagues/23172/players?season=2021&statType=1&sortMode=1&position=511&isFreeAgent=false&tableSortDirection=DESC&tableSortName=pv7&tableOffset='

	players = []
	for baseurl in [hitter_base_url, pitcher_base_url]:
		for i in range(0, 401, 20):
			url = baseurl + str(i)
			page = requests.get(url)
			time.sleep(1)
			soup = BeautifulSoup(page.text, 'html.parser')
			table = soup.find('div', {'id':'body-center-main'}).find('table')

			count = 0
			trow = table.find('thead').next_sibling
			while trow is not None and count<20:
				player_data = trow.find('div', {'class':'player'})
				player_name = unidecode.unidecode(player_data.find('a', {'class':'player-text'}).text)
				player_id = player_data.find('a', {'class':'player-text'})['href'].split('/')[-1].split('-')[-1]
				elig = player_data.find('span', {'class':'position'}).text
				#print('  '.join([player_name, player_id, elig]))
				players.append([player_name, player_id, elig])
				trow = trow.next_sibling
				count = count+1

	df_players = pd.DataFrame(players, columns=['Player','ff_id','ff_elig'])

	def combine_eligibilities(row):
		ff_elig_list = row['ff_elig'].split('/')
		print(row['Player'])
		print(row['ff_elig'])
		print(ff_elig_list)
		eligibilities = []

		# Infielders
		for pos in ['C', '1B', '2B', 'SS', '3B']:
			if pos in ff_elig_list:
				eligibilities.append(pos)
		if '2B' in eligibilities or 'SS' in eligibilities:
			eligibilities.append('MI')
		if '1B' in eligibilities or '3B' in eligibilities:
			eligibilities.append('CI')
		if 'MI' in eligibilities or 'CI' in eligibilities:
			eligibilities.append('IF')

		# Outfielders
		for pos in ['OF', 'RF', 'LF', 'CF']:
			if pos in ff_elig_list and 'OF' not in eligibilities:
				eligibilities.append('OF')

		# Pitchers - just use the same as FF
		if 'SP' in eligibilities or 'RP' in eligibilities or 'P' in eligibilities:
			eligibilities = ff_elig_list

		print(eligibilities)
		# Concatenate into a string and return
		elig = ' '.join(eligibilities).strip()
		print(elig)
		if elig == '':
			elig = 'UT'
		return elig

	df_players['elig'] = df_players.apply(lambda row: combine_eligibilities(row), axis=1)

	names = player_names.get_player_names()
	df_players = df_players.merge(right=names[['ff_id', 'fg_id']], how='left', on='ff_id')

	bbdb = postgres.connect_to_bbdb()
	df_players.to_sql('player_names_ff', con=bbdb, schema='reference', if_exists='replace', chunksize=1000, method='multi', index=False)

	return df_players


def push_ff_names_to_gs():
	import sys
	sys.path.append('python/general')
	import postgres
	import pandas as pd
	import gspread
	import gspread_dataframe as gsdf

	bbdb = postgres.connect_to_bbdb()
	ff_names = pd.read_sql('SELECT * FROM reference.player_names_ff', con=bbdb)
	gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
	sh = gc.open("BB 2021 Name Matching").worksheet('FF match')
	gsdf.set_with_dataframe(sh, ff_names)




def push_player_names_to_gs():
	import sys
	sys.path.append('python/general')
	import postgres
	import pandas as pd
	import gspread
	import gspread_dataframe as gsdf

	bbdb = postgres.connect_to_bbdb()
	player_names = pd.read_sql('SELECT * FROM reference.player_names', con=bbdb)
	gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
	sh = gc.open("BB 2021 Name Matching").worksheet('Player Names')
	gsdf.set_with_dataframe(sh, player_names)


def pull_player_names_from_gs():
	bbdb = postgres.connect_to_bbdb()
	gc = gspread.service_account(filename='./bb-2021-2b810d2e3d25.json')
	sh = gc.open("BB 2021 Name Matching").worksheet('Player Names')
	player_names = gsdf.get_as_dataframe(sh)

	# convert any numeric ids into text
	for col in ['fg_id', 'otto_id', 'yahoo_id', 'bp_id', 'espn_id', 'ff_id', 'mlb_id']:
		if col in player_names.columns:
			player_names[col] = player_names[col].astype('str').replace('\.0', '', regex=True)

	colnames = player_names.columns.tolist()
	player_names.columns = colnames

	command = 'TRUNCATE TABLE reference.player_names'
	bbdb.execute(command)
	player_names.to_sql('player_names', bbdb, schema='reference', if_exists='append', chunksize=1000, method='multi', index=False)


def scrape_sfb_names():
	import os
	import pandas as pd
	import selenium_utilities

	# Download the latest .csv file from smartfantasybaseball.com
	driver = selenium_utilities.start_driver()
	driver.get("https://www.smartfantasybaseball.com/PLAYERIDMAPCSV")
	filename = '/Users/andrewfelton/Downloads/docker/SFBB Player ID Map - PLAYERIDMAP.csv'
	sfb_names = pd.read_csv(filename, dtype=str)
	os.remove(filename)


	orignames = list(sfb_names.columns.values)
	colnames = list(sfb_names.columns.values)
	colmap = dict()
	for i in range(0, len(colnames)):
		colnames[i] = colnames[i].lower()
		if colnames[i][-2:]=='id':
			colnames[i] = colnames[i][:-2]+'_id'
		if colnames[i][:2]=='id':
			colnames[i] = colnames[i][2:]+'_id'
		if colnames[i][-4:]=='name':
			colnames[i] = colnames[i][:-4]+'_name'
		colnames[i] = colnames[i].replace('fangraphs','fg')
		colmap[orignames[i]] = colnames[i]
	sfb_names = sfb_names.rename(mapper=colmap, axis=1)

	tablename = 'player_names_sfb'
	bbdb = postgres.connect_to_bbdb()
	command = 'TRUNCATE TABLE reference.' + tablename
	bbdb.execute(command)
	sfb_names.to_sql(tablename, bbdb, schema='reference', if_exists='append')

