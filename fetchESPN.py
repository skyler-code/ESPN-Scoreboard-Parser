from os import getenv
from urllib.request import build_opener

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

COOKIE_STR = getenv("COOKIE_STR")
LEAGUE_ID = getenv("LEAGUE_ID")

def getData(url):
    opener = build_opener()
    opener.addheaders.append(('Cookie', COOKIE_STR))
    response = opener.open(url)
    data = response.read()
    text = data.decode('utf-8')
    soup = BeautifulSoup( text, features='html.parser' )
    return soup

class fetch:
    def fetchScoreboard(TEAM_ID, WEEK_ID, SEASON_ID):
        url = ('http://games.espn.com/ffl/boxscorequick?leagueId=%s&teamId=%s&scoringPeriodId=%s&seasonId=%s&view=scoringperiod&version=quick' % (LEAGUE_ID, TEAM_ID, WEEK_ID, SEASON_ID))
        return getData(url)
    
    def fetchSchedule(SEASON_ID):
        url = ('http://games.espn.com/ffl/schedule?leagueId=%s&seasonId=%s' % (LEAGUE_ID, SEASON_ID))
        return getData(url)
