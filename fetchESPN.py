from os import getenv
from urllib.request import build_opener

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

COOKIE_STR = getenv("COOKIE_STR")
LEAGUE_ID = getenv("LEAGUE_ID")
SEASON_ID = getenv("SEASON_ID")

ESPN_ROOT_URL = 'http://games.espn.com/ffl/'

def getData(url):
    opener = build_opener()
    opener.addheaders.append(('Cookie', COOKIE_STR))
    response = opener.open(url)
    data = response.read()
    text = data.decode('utf-8')
    soup = BeautifulSoup( text, features='html.parser' )
    return soup

class fetch:

    def __init__(self):
        pass

    def fetchScoreboard(self, teamId, weekId):
        url = ESPN_ROOT_URL + ('boxscorequick?leagueId=%s&teamId=%s&scoringPeriodId=%s&seasonId=%s&view=scoringperiod&version=quick' % (LEAGUE_ID, teamId, weekId, SEASON_ID))
        return getData(url)
    
    def fetchSchedule(self):
        url = ESPN_ROOT_URL + ('schedule?leagueId=%s&seasonId=%s' % (LEAGUE_ID, SEASON_ID))
        return getData(url)
