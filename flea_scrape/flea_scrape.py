from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import os
import datetime

pg_rosters = get('https://www.fleaflicker.com/mlb/leagues/21579/teams')

bs_rosters = BeautifulSoup(pg_rosters.text, features='html.parser')




def print_players(trow, league_name, roster_file):
	player_row = trow
	while not (player_row.has_attr('class') and player_row['class'][0]=="last"):
		player = player_row.find('div', class_='player')
		player_name = player.find('a', class_='player-text')
		print(league_name + "\t" + player_name.string)
		roster_file.write(league_name + "\t" + player_name.string + "\n")
		player_row = player_row.next_sibling
	roster_file.flush()
	return player_row


def loop_through_rows(trow):
	while trow is not None:
		# loop through the rows looking for a <span> with class_="league-name"
		while trow is not None and not(trow.find("span", class_="league-name")):
			trow = trow.next_sibling
		if trow is not None:
			name_row = trow
			league_name = trow.find("span", class_="league-name").text
			print("\n\n*******" + league_name + "*******")
			league_names.append(league_name)
			trow=trow.next_sibling
			trow = print_players(trow, league_name, roster_file)
			#print(trow)





main_div = bs_rosters.find('div', id='body-center-main')
tables = main_div.find_all('table')

today = datetime.date.today()
str_today = str(today)

file_rosters = '/Users/andrewfelton/Downloads/rosters_'+str_today+'.txt'
print('Saving rosters to ' + file_rosters)
roster_file = open(file_rosters, 'w')
for i in range(0,2):
	print("\n\n------------" + str(i) + "------------")
	t = tables[i]
	#print(t)
	thead = t.find('thead')
	league_name = thead.find("span", class_="league-name").text
	league_names = [league_name]
	trow = thead.next_sibling
	trow = print_players(trow, league_name, roster_file)
	#used for debugging
	temp = trow
	#trow=temp
	loop_through_rows(trow)


#print(league_names)
roster_file.close

os.system("open " + file_rosters)



