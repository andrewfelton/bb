from python.utilities import selenium_utilities
import time
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata

def scrape_bbref(urlprefix, year, urlsuffix, tableid):

    sys.path.append('python/utilities')
    import selenium_utilities
    driver = selenium_utilities.start_driver()

    #urlprefix = 'https://www.baseball-reference.com/leagues/MLB/'
    #year = '2020'
    #urlsuffix = '-appearances-fielding.shtml'
    #tableid = 'players_players_appearances_fielding'
    #url = 'https://www.baseball-reference.com/leagues/MLB/2020-appearances-fielding.shtml'
    url = urlprefix + str(year) + urlsuffix


    # Log in
    driver.get("https://stathead.com/users/login.cgi?token=1&redirect_uri=https%3A//www.baseball-reference.com/")
    time.sleep(2)
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
    print("Arrived at "+url)

    # Copy the HTML into BS
    soup = BeautifulSoup(driver.page_source, 'lxml')
    mytable = soup.find(id=tableid)
    trs = mytable.find_all("tr")
    colnames = ['bbref_id']
    for th in trs[0].find_all("th"):
        colnames.append(th.text)
    del(colnames[1])

    players = []
    errors = []
    for tr in trs[1:]:
        playerdata = []
        try:
            if (tr.get_attribute_list("class") != 'thead'):
                tds = tr.find_all("td")
                playerdata.append(tds[0].get_attribute_list('data-append-csv')[0])
                playerdata.append(unicodedata.normalize('NFKD', tds[0].text)) # get rid of \xa0 (nonbreaking space) characters
                for td in tds[1:]:
                    playerdata.append(td.text)
                players.append(playerdata)
        except IndexError:
            errors.append(tr)

    players = pd.DataFrame(data=players, columns=colnames)
    players.insert(0, 'year', year)

    return players

    # Close it down
    driver.close()
    selenium_utilities.stop_selenium('bbsel')



if (1==2):
    urlprefix = 'https://www.baseball-reference.com/leagues/MLB/'
    urlsuffix = '-appearances-fielding.shtml'
    tableid = 'players_players_appearances_fielding'

    positions2020 = scrape_bbref(urlprefix, 2020, urlsuffix, tableid)
    positions2020.to_sql('positions', bbdb, schema='reference', if_exists='replace')
    for y in range(2010,2019):
        positions = scrape_bbref(urlprefix, y, urlsuffix, tableid)
        positions.to_sql('positions', bbdb, schema='reference', if_exists='append')



import postgres



