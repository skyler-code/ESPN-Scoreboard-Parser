import urllib.parse as urlparse
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
from os import getenv

from dotenv import load_dotenv
from pydash import replace_end

from fetchESPN import fetch
from printSpreadsheet import printSpreadsheet

load_dotenv()
SEASON_ID = getenv("SEASON_ID")
fetchESPN = fetch()

def parseQueryString( queryStr:str ):
    return urlparse.parse_qs(urlparse.urlparse(queryStr).query)

def getLeagueInfo():
    scheduleSoup = fetchESPN.fetchSchedule()
    leagueName = replace_end(scheduleSoup.title.text,' Schedule -  ESPN', '')
    print( "Beginning parse of %s's %s season..." % (leagueName, SEASON_ID) )

    teamInfo, schedule = dict(), OrderedDict()
    links = scheduleSoup.find('table', class_='tableBody').find_all('a', href=True)
    for a in links:
        url = a['href']
        if 'boxscorequick' in url:
            query_def = parseQueryString(url)
            teamId = query_def['teamId'][0]
            scoringPeriodId = query_def['scoringPeriodId'][0]
            if scoringPeriodId not in schedule:
                schedule[scoringPeriodId] = []
            schedule[scoringPeriodId].append(teamId)
        elif 'clubhouse' in url:
            query_def = parseQueryString(url)
            teamId = query_def['teamId'][0]
            if teamId not in teamInfo:
                teamInfo[teamId] = a['title']
    return schedule, leagueName, teamInfo

def getScoreInfo( scoreSoup ):
    d = dict()
    currentIndex = 0
    totalScores = scoreSoup.find_all('div', class_='totalScore')
    benchScores = scoreSoup.select('div[id*="tmInactivePts"]')
    teamNames = scoreSoup.find('div', id='teamInfos').find_all('a')
    for team in teamNames:
        teamId = parseQueryString(team['href'])['teamId'][0]
        d[teamId] = dict()
        starterPoints = Decimal(totalScores[currentIndex]['title'])
        benchPoints = Decimal(benchScores[currentIndex].text if len(benchScores) > 0 else 0)
        d[teamId]['starter'] = starterPoints
        d[teamId]['bench'] = benchPoints
        d[teamId]['total'] = starterPoints + benchPoints
        currentIndex += 1
    return d

def parseLeagueResults( weeks:OrderedDict ):
    leagueResults = OrderedDict()
    for week in weeks:
        print('Parsing week %s...' % (week), end='', flush=True)
        leagueResults[week] = []
        for teamId in weeks[week]:
            scoreboardText = fetchESPN.fetchScoreboard(teamId, week)
            scoreInfo = getScoreInfo(scoreboardText)
            leagueResults[week].append(scoreInfo)
        print('DONE')
    return leagueResults

def main():
    scheduleInfo, leagueName, teamInfo = getLeagueInfo()
    leagueResults = parseLeagueResults(scheduleInfo)
    spreadsheet = printSpreadsheet(teamInfo, leagueName, leagueResults, scheduleInfo)
    spreadsheet.printSpreadsheet()

main()
