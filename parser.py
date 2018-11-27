from datetime import datetime
from fetchESPN import fetch
from bs4 import BeautifulSoup
from decimal import Decimal

SEASON_ID = datetime.now().year
NUM_TEAMS = 10
MAX_WEEKS = 12

TEAM_IDS = []

def getScoreInfo( score ):
    d = dict()
    scoreSoup = BeautifulSoup( score, features='html.parser' )
    teamName = scoreSoup.find_all('tr', class_='playertableTableHeader')[0].text.replace(' Box Score', '')
    boxscores = scoreSoup.find_all('div', class_='totalScore')
    actualPoints = Decimal(boxscores[0]['title'])
    benchPoints = Decimal(boxscores[1]['title'])
    totalPoints = actualPoints + benchPoints
    d['teamName'] = teamName
    d['actualPoints'] = str(actualPoints)
    d['benchPoints'] = str(benchPoints)
    d['totalPoints'] = str(totalPoints)
    return d

membersText = fetch.fetchMembers()
membersSoup = BeautifulSoup( membersText, features='html.parser' )
teams = membersSoup.find_all('td', class_='teamName')
for team in teams:
    vals = team.a['href'].split('&')
    TEAM_IDS.append(vals[1].replace('teamId=', ''))

for teamId in TEAM_IDS:
    for week in range(1, MAX_WEEKS+1):
        scoreboardText = fetch.fetchScoreboard(teamId, week, SEASON_ID)
        scoreInfo = getScoreInfo(scoreboardText)
        outputStr = ('Week: %s Info: %s' % (week, scoreInfo))
        print(outputStr)


#testOutput = ('Team name: %s<br/>Week: %s<br/>Points: %s<br/>Bench: %s<br/>Total points: %s' % (teamName, WEEK_ID, actualPoints, benchPoints, totalPoints))

#print(testOutput.replace('style="display:none;"', ''), file=open('test.html', 'w'))
#print(teamName)