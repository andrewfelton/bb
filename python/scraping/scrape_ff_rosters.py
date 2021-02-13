def scrape_ff_rosters():
    import sys
    sys.path.append('/python')
    import selenium_utilities
    import time
    import datetime
    from bs4 import BeautifulSoup

    driver = selenium_utilities.start_driver()

    driver.get("https://www.fleaflicker.com/mlb/login")
    time.sleep(2)
    driver.current_url

    input_login = driver.find_element_by_name('email')
    input_login.send_keys('andy.felton@gmail.com')
    input_pw = driver.find_element_by_name('password')
    input_pw.send_keys('9X7@eCmF$ZMb')
    input_submit = driver.find_element_by_xpath('//*[@id="body-center-main"]/form/div/div[2]/button')
    input_submit.click()
    time.sleep(2)

    driver.current_url
    
    roster_url = 'https://www.fleaflicker.com/mlb/leagues/23172/teams'
    driver.get(roster_url)


    bs_rosters = BeautifulSoup(driver.page_source, 'lxml')
    main_div = bs_rosters.find('div', id='body-center-main')
    tables = main_div.find_all('table')

    today = datetime.date.today()
    str_today = str(today)

    for table in tables:
        print(table)


    t = tables[0]
    # The first team's name is in the thead, the rest are in tbody
    thead = t.find('thead')
    team_name = thead.find("span", class_="league-name").text
    team_names = [league_name]


    class team:
        def __init__(self, name):  
            self.name = name 
            players = []

    class player:
        def __init__(self, name):  
            self.name = name
            ff_id = None


    teams = []
    teams.append( team(team_name) )
    current_team = teams[-1]


    # Loop through the tbody
    tbody = t.find('tbody')
    trows = tbody.find_all('tr')
    for tr in trows
    tr = trows[0]
        player_data = tr.find('a', {"class": "player-text"})
        player_data.text
        current_team.players.append(player(player_data.text))








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



