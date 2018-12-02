import urllib.parse as urlparse
from datetime import datetime
from decimal import Decimal
from os import makedirs, path

from pydash import replace_end

from fetchESPN import fetch

SEASON_ID = datetime.now().year

def parseQueryString( queryStr:str ):
    return urlparse.parse_qs(urlparse.urlparse(queryStr).query)


def getScheduleInfo():
    scheduleSoup = fetch.fetchSchedule(SEASON_ID)
    leagueName = replace_end(scheduleSoup.title.text,' Schedule -  ESPN', '')
    print( "Beginning parse of %s's %s season..." % (leagueName, SEASON_ID) )

    schedule = dict()
    rows = scheduleSoup.find_all('a', href=True)
    for r in rows:
        if 'boxscorequick' in r['href']:
            query_def = parseQueryString(r['href'])
            teamId = query_def['teamId'][0]
            scoringPeriodId = query_def['scoringPeriodId'][0]
            if scoringPeriodId not in schedule:
                schedule[scoringPeriodId] = []
            schedule[scoringPeriodId].append(teamId)
    return schedule, leagueName

def getScoreInfo( scoreSoup ):
    d = dict()
    currentIndex = 0
    totalScores = scoreSoup.find_all('div', class_='totalScore')
    benchScores = scoreSoup.select('div[id*="tmInactivePts"]')
    teamNames = scoreSoup.find('div', id='teamInfos').find_all('a')
    for team in teamNames:
        query_def = parseQueryString(team['href'])
        teamId = query_def['teamId'][0]
        d[teamId] = dict()
        actualPoints = Decimal(totalScores[currentIndex]['title'])
        benchPoints = Decimal(benchScores[currentIndex].text if len(benchScores) > 0 else 0)
        d[teamId]['actual'] = float(actualPoints)
        d[teamId]['bench'] = float(benchPoints)
        d[teamId]['total'] = float(actualPoints + benchPoints)
        currentIndex += 1
    return d

def parseLeagueResults( weeks:dict ):
    leagueResults = dict()
    for week in weeks:
        print('Parsing week %s...' % (week), end='', flush=True)
        leagueResults[week] = []
        for teamId in weeks[week]:
            scoreboardText = fetch.fetchScoreboard(teamId, week, SEASON_ID)
            scoreInfo = getScoreInfo(scoreboardText)
            leagueResults[week].append(scoreInfo)
        print('DONE')
    return leagueResults

def printResults( leagueName:str, leagueResults:dict ):
    resultDirectory = 'results'
    outputFileName = ('%s/%s-%s.txt' % (resultDirectory, leagueName.replace(' ', '-'), SEASON_ID))
    print('Printing to %s...' % (outputFileName), end='', flush=True)
    if not path.exists(resultDirectory):
        makedirs(resultDirectory)
    print(leagueResults, file=open(outputFileName, 'w'))
    print('DONE')

def main():
    scheduleInfo, leagueName = getScheduleInfo()
    leagueResults = parseLeagueResults(scheduleInfo)
    printResults(leagueName, leagueResults)

main()
