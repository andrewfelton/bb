import sys
sys.path.append('python/general')
import selenium_utilities
import postgres
import time
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata

def scrape_bbref(urlprefix, year, urlsuffix, tableid):
    driver = selenium_utilities.start_driver()
    #urlprefix = 'https://www.baseball-reference.com/leagues/MLB/'
    #year = '2020'
    #urlsuffix = '-appearances-fielding.shtml'
    #tableid = 'players_players_appearances_fielding'
    #url = 'https://www.baseball-reference.com/leagues/MLB/2020-appearances-fielding.shtml'
    url = urlprefix + str(year) + urlsuffix
    print('Going to scrape '+url)

    # Log in
    driver.get('https://stathead.com/users/login.cgi?token=1&redirect_uri=https%3A//www.baseball-reference.com/')
    time.sleep(2)
    print(driver.current_url)
    if driver.current_url!='https://www.baseball-reference.com/':
        input_login = driver.find_element_by_id('username')
        input_login.send_keys('afelton')
        input_pw = driver.find_element_by_id('password')
        input_pw.send_keys('#aR2g%!JcNd$yHkC&GG0')
        input_submit = driver.find_element_by_xpath('//*[@id="content"]/form/div[4]/div/input')
        input_submit.click()
        time.sleep(2)

    # Go to the projections page
    driver.get(url)
    time.sleep(5)
    print('Arrived at '+url)

    # Copy the HTML into BS
    soup = BeautifulSoup(driver.page_source, 'lxml')
    mytable = soup.find(id=tableid)
    trs = mytable.find_all('tr')
    colnames = ['bbref_id']
    for th in trs[0].find_all('th'):
        colnames.append(th.text)
    del(colnames[1])

    players = []
    errors = []
    for tr in trs[1:]:
        playerdata = []
        try:
            if (tr.get_attribute_list('class') != 'thead'):
                tds = tr.find_all('td')
                playerdata.append(tds[0].get_attribute_list('data-append-csv')[0])
                playerdata.append(unicodedata.normalize('NFKD', tds[0].text)) # get rid of \xa0 (nonbreaking space) characters
                for td in tds[1:]:
                    playerdata.append(td.text)
                players.append(playerdata)
        except IndexError:
            errors.append(tr)

    players = pd.DataFrame(data=players, columns=colnames)
    players.insert(0, 'year', year)

    # Close it down
    driver.close()
    return players


if (1==2):
    urlprefix = 'https://www.baseball-reference.com/leagues/MLB/'
    urlsuffix = '-appearances-fielding.shtml'
    tableid = 'players_players_appearances_fielding'
    bbdb = postgres.connect_to_bbdb()

    positions2020 = scrape_bbref(urlprefix, 2020, urlsuffix, tableid)
    positions2020.to_sql('positions', bbdb, schema='reference', if_exists='replace')
    for y in range(2010,2019):
        positions = scrape_bbref(urlprefix, y, urlsuffix, tableid)
        positions.to_sql('positions', bbdb, schema='reference', if_exists='append')

    urlprefix = 'https://www.baseball-reference.com/leagues/MLB/'
    urlsuffix = '-standard-batting.shtml'
    tableid = 'players_standard_batting'

    batting_2021 = scrape_bbref(urlprefix, 2021, urlsuffix, tableid)
    batting_2021.to_sql('positions', bbdb, schema='reference', if_exists='replace')

    urlsuffix = '-standard-pitching.shtml'
    tableid = 'players_standard_pitching'
    pitching_standard_2021 = scrape_bbref(urlprefix, 2021, urlsuffix, tableid)
    pitching_standard_2021[["year", "bbref_id", "Name", "Age", "Tm", "Lg", "W", "L", "ERA", "G", "GS", "GF", "CG", "SHO", "SV", "IP", "H", "R", "ER", "HR", "BB", "IBB", "SO", "HBP", "BK", "WP", "BF", "FIP", "WHIP", "H9", "HR9", "BB9", "SO9"]].to_sql('bbref_pitching_standard', bbdb, schema='reference', if_exists='replace')

    urlsuffix = '-starter-pitching.shtml'
    tableid = 'players_starter_pitching'
    pitching_starter_2021 = scrape_bbref(urlprefix, 2021, urlsuffix, tableid)
    pitching_starter_2021[['year', 'bbref_id', 'Name', 'Age', 'Tm', 'IP', 'G', 'GS', 'Wgs', 'Lgs', 'ND', 'Wchp', 'Ltuf', 'Wtm', 'Ltm', 'Wlst', 'Lsv', 'CG','SHO', 'QS', 'GmScA', 'Best', 'Wrst', 'BQR', 'BQS', 'sDR', 'lDR']].to_sql('bbref_pitching_starter', bbdb, schema='reference', if_exists='replace')

    urlsuffix = '-reliever-pitching.shtml'
    tableid = 'players_reliever_pitching'
    pitching_reliever_2021 = scrape_bbref(urlprefix, 2021, urlsuffix, tableid)
    pitching_reliever_2021[['year', 'bbref_id', 'Name', 'Age', 'Tm', 'IP', 'G', 'GS', 'Wgs', 'Lgs', 'ND', 'Wchp', 'Ltuf', 'Wtm', 'Ltm', 'Wlst', 'Lsv', 'CG','SHO', 'QS', 'GmScA', 'Best', 'Wrst', 'BQR', 'BQS', 'sDR', 'lDR']].to_sql('bbref_pitching_reliever', bbdb, schema='tracking', if_exists='replace')


def scrape_actuals(year=2021):
    bbdb = postgres.connect_to_bbdb()

    urlprefix = 'https://www.baseball-reference.com/leagues/MLB/'

    urlsuffix = '-standard-batting.shtml'
    tableid = 'players_standard_batting'
    batting_2021 = scrape_bbref(urlprefix, 2021, urlsuffix, tableid)
    batting_2021[['year', 'bbref_id', 'Name', 'Age', 'Tm', 'Lg', 'G', 'PA', 'AB', 'R', 'H', 'HR', 'RBI', 'SB', 'CS', 'BB', 'SO', 'BA', 'OBP', 'SLG', 'OPS', 'TB', 'GDP', 'HBP', 'SH', 'SF', 'IBB']].to_sql('bbref_batting_standard', bbdb, schema='tracking', if_exists='replace')

    urlsuffix = '-standard-pitching.shtml'
    tableid = 'players_standard_pitching'
    pitching_standard_2021 = scrape_bbref(urlprefix, 2021, urlsuffix, tableid)
    pitching_standard_2021[["year", "bbref_id", "Name", "Age", "Tm", "Lg", "W", "L", "ERA", "G", "GS", "GF", "CG", "SHO", "SV", "IP", "H", "R", "ER", "HR", "BB", "IBB", "SO", "HBP", "BK", "WP", "BF", "FIP", "WHIP", "H9", "HR9", "BB9", "SO9"]].to_sql('bbref_pitching_standard', bbdb, schema='tracking', if_exists='replace')

    urlsuffix = '-starter-pitching.shtml'
    tableid = 'players_starter_pitching'
    pitching_starter_2021 = scrape_bbref(urlprefix, 2021, urlsuffix, tableid)
    pitching_starter_2021[['year', 'bbref_id', 'Name', 'Age', 'Tm', 'IP', 'G', 'GS', 'Wgs', 'Lgs', 'ND', 'Wchp', 'Ltuf', 'Wtm', 'Ltm', 'Wlst', 'Lsv', 'CG','SHO', 'QS', 'GmScA', 'Best', 'Wrst', 'BQR', 'BQS', 'sDR', 'lDR']].to_sql('bbref_pitching_starter', bbdb, schema='tracking', if_exists='replace')

    urlsuffix = '-reliever-pitching.shtml'
    tableid = 'players_reliever_pitching'
    pitching_reliever_2021 = scrape_bbref(urlprefix, 2021, urlsuffix, tableid)
    pitching_reliever_2021[['year', 'bbref_id', 'Name', 'Age', 'Tm', 'IP', 'G', 'GR', 'GF', 'Wgr', 'Lgr', 'SVOpp', 'SV', 'BSv', 'SVSit', 'Hold', 'IR', 'IS', 'aLI', 'LevHi', 'LevMd', 'LevLo', 'Ahd', 'Tie', 'Bhd', 'Runr']].to_sql('bbref_pitching_reliever', bbdb, schema='tracking', if_exists='replace')









