from bs4 import BeautifulSoup
from datetime import date
import datetime
import urllib2
import re
import json
import time



def getGameIds (start_date, end_date, league_name, league_id):

    game_ids = set()

    iter_date = start_date
    delta = datetime.timedelta(days=1)

    counter = 0

    while iter_date <= end_date:

        counter += 1

        url = "http://www.espnfc.com/" + league_name + "/" + str(league_id) \
              + "/scores?date=" + iter_date.strftime("%Y%m%d")
        print counter, url

        if (counter % 30 == 0):
            print 'TIMEOUT! Sleeping for 30 minutes...'
            time.sleep(60*30)

        page = urllib2.urlopen(url, timeout=10)
        while (page.getcode()!=200):
            print 'HTML Error! code: ' + str(page.getcode())
            print 'Sleeping for 10 minutes...'
            time.sleep(60 * 10)
            page = urllib2.urlopen(url, timeout=10)

        soup = BeautifulSoup(page, "html.parser")
        gamelines = soup.find_all("div", {"class": "score full"})
        # gameids = soup.find_all("div", {"data-gameId":True})

        for gameline in gamelines:
            game_id = gameline.prettify()[37:43]
            print game_id
            game_ids.add(game_id)

        # print game_ids

        iter_date += delta

    return game_ids



def getReport (game_id):

    url = "http://www.espnfc.com/report?gameId=" + str(game_id)
    page = urllib2.urlopen(url)

    soup = BeautifulSoup(page, "html.parser")

    report = soup.find("div", {"id": "article-feed"})
    report_title = report.find("h1").text
    report_text = str(report.find_all("p")).replace("<p>", "").replace("</p>", "")

    print report_title, report_text
    return report_title, report_text



def getCommentary_all (game_id):

    url = "http://www.espnfc.com/commentary?gameId=" + str(game_id)
    page = urllib2.urlopen(url)

    soup = BeautifulSoup(page, "html.parser")
    #comments = soup.find_all("tr", {"data-type": True})
    comments = soup.find_all("tr", {"data-type": True})

    for comment in comments:
        print ''
        print comment.find("td", {"class": "time-stamp"}).text.strip()
        print comment["data-type"]
        print comment.find("td", {"class": "game-details"}).text.strip()

    return None



def getCommentary_key (game_id):

    url = "http://www.espnfc.com/commentary?gameId=" + str(game_id)
    page = urllib2.urlopen(url)

    soup = BeautifulSoup(page, "html.parser")
    #comments = soup.find_all("tr", {"data-type": True})
    comments = soup.find_all("li", {"data-key-event-ids": True})

    for comment in comments:
        print ''
        print comment["data-time"]
        print comment.find("li", {"class": "events-of-type"})["data-events-type"]
        print comment.find("ul", {"class": "details"})["data-event-home-away"]
        print comment.find("div", {"class": "detail"}).text.strip()

    return None



def getGameStats (game_id):

    url = "http://www.espnfc.com/matchstats?gameId=" + str(game_id)
    page = urllib2.urlopen(url)

    soup = BeautifulSoup(page, "html.parser")

    home_fouls = soup.find("td", {"data-home-away": "home", "data-stat" : "foulsCommitted"}).text
    home_yellows = soup.find("td", {"data-home-away": "home", "data-stat" : "yellowCards"}).text
    home_reds = soup.find("td", {"data-home-away": "home", "data-stat" : "redCards"}).text
    home_offsides = soup.find("td", {"data-home-away": "home", "data-stat" : "offsides"}).text
    home_corners = soup.find("td", {"data-home-away": "home", "data-stat" : "wonCorners"}).text
    home_saves =  soup.find("td", {"data-home-away": "home", "data-stat" : "saves"}).text
    home_shotsSummary = soup.find("span", {"data-home-away": "home", "data-stat": "shotsSummary"}).text
    home_shots = home_shotsSummary.split(" ")[0]
    home_goals = home_shotsSummary.split(" ")[1].replace("(","").replace(")","")
    home_possession = soup.find("span", {"class": "chartValue", "data-home-away": "home", "data-stat": "possessionPct"}).text

    away_fouls = soup.find("td", {"data-home-away": "away", "data-stat": "foulsCommitted"}).text
    away_yellows = soup.find("td", {"data-home-away": "away", "data-stat": "yellowCards"}).text
    away_reds = soup.find("td", {"data-home-away": "away", "data-stat": "redCards"}).text
    away_offsides = soup.find("td", {"data-home-away": "away", "data-stat": "offsides"}).text
    away_corners = soup.find("td", {"data-home-away": "away", "data-stat": "wonCorners"}).text
    away_saves = soup.find("td", {"data-home-away": "away", "data-stat": "saves"}).text
    away_shotsSummary = soup.find("span", {"data-home-away": "away", "data-stat": "shotsSummary"}).text
    away_shots = away_shotsSummary.split(" ")[0]
    away_goals = away_shotsSummary.split(" ")[1].replace("(","").replace(")","")
    away_possession = soup.find("span", {"class": "chartValue", "data-home-away": "away", "data-stat": "possessionPct"}).text

    print home_fouls, home_yellows, home_reds, home_offsides, home_corners, home_saves, \
        home_shots, home_goals, home_possession
    print away_fouls, away_yellows, away_reds, away_offsides, away_corners, away_saves, \
        away_shots, away_goals, away_possession

    return None
    # http://www.espnfc.com/matchstats?gameId=450998



def getPlayerStatDetails (players_content):

    players = players_content.find_all("div", {"class": "accordion-item"})

    for player in players:

        name = player.find("a", href=re.compile("^http://espnfc.com/player/")).text
        link = player.find("a", href=re.compile("^http://espnfc.com/player/"))["href"]

        saves = getattr(player.find("span", {"data-stat": "saves"}), "text", "0")
        shots = getattr(player.find("span", {"data-stat": "totalShots"}), "text", "0")
        goals = getattr(player.find("span", {"data-stat": "shotsOnTarget"}), "text", "0")
        goal_assists = getattr(player.find("span", {"data-stat": "goalAssists"}), "text", "0")

        fouls_committed = getattr(player.find("span", {"data-stat": "foulsCommitted"}), "text", "0")
        fouls_suffered = getattr(player.find("span", {"data-stat": "foulsSuffered"}), "text", "0")
        offsides = getattr(player.find("span", {"data-stat": "offsides"}), "text", "0")
        yellows = getattr(player.find("span", {"data-stat": "yellowCards"}), "text", "0")
        reds = getattr(player.find("span", {"data-stat": "redCards"}), "text", "0")

        print name, link, \
            saves, shots, goals, goal_assists, \
            fouls_committed, fouls_suffered, offsides, yellows, reds



def getPlayerStats (game_id):

    url = "http://www.espnfc.com/lineups?gameId=" + str(game_id)
    page = urllib2.urlopen(url)

    soup = BeautifulSoup(page, "html.parser")

    # Retrieving home and away team tables
    teams = soup.find_all('table', {"data-behavior":"table_accordion"})
    team_home = teams[0]
    team_away = teams[1]

    # Retrieving main and substitute players for home and away teams
    players_main_home = team_home.find_all("tbody")[0]
    players_sub_home = team_home.find_all("tbody")[1]
    players_main_away = team_away.find_all("tbody")[0]
    players_sub_away = team_away.find_all("tbody")[1]

    getPlayerStatDetails(players_main_home)
    getPlayerStatDetails(players_sub_home)
    getPlayerStatDetails(players_main_away)
    getPlayerStatDetails(players_sub_away)

    return None



# EPL 16/17 season is from 2016-08-13 to 2017-05-21
#start_date = date(2016, 8, 13)
start_date = date(2017, 5, 9)
end_date = date(2017, 5, 21)
league_name = 'english-premier-league'
league_id = 23

# Retrieveing all game ids for the given season
game_ids = getGameIds(start_date, end_date, league_name, league_id)
json_str = json.dumps(list(game_ids))
print json_str

f = open('/Users/anlab/Desktop/game_ids.txt', 'w')
f.write(json_str)
f.close()



# Retrieving reports and stats for each game

# for game_id in game_ids:
    #getReport(game_id) # Retrieveing news articles
    #getCommentary_all(game_id) # Retrieving comments on all events
    #getCommentary_key(game_id) # Retrieving comments on key events
    #getGameStats(game_id) # Retrieving overall game stats
    #getPlayerStats(game_id) # Retrieving player stats