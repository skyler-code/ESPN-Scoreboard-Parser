from datetime import datetime
from fetchESPN import fetch
from decimal import Decimal

SEASON_ID = datetime.now().year
NUM_TEAMS = 10
MAX_WEEKS = 12

def getScoreInfo( scoreSoup ):
    d = dict()
    boxscores = scoreSoup.find_all('div', class_='totalScore')
    d['teamName'] = scoreSoup.find_all('tr', class_='playertableTableHeader')[0].text.replace(' Box Score', '')
    d['actualPoints'] = boxscores[0]['title']
    d['benchPoints'] = boxscores[1]['title']
    d['totalPoints'] = str(Decimal(d['actualPoints']) + Decimal(d['benchPoints']))
    return d

membersSoup = fetch.fetchMembers()
teams = membersSoup.find_all('td', class_='teamName')
TEAM_IDS = []
for team in teams:
    vals = team.a['href'].split('&')
    TEAM_IDS.append(vals[1].replace('teamId=', ''))

for teamId in TEAM_IDS:
    for week in range(1, MAX_WEEKS+1):
        scoreboardText = fetch.fetchScoreboard(teamId, week, SEASON_ID)
        scoreInfo = getScoreInfo(scoreboardText)
        outputStr = ('Week: %s Info: %s' % (week, scoreInfo))
        print(outputStr)
 