from datetime import datetime
from decimal import Decimal
from os import makedirs, path
from pydash import replace_end

from fetchESPN import fetch

SEASON_ID = datetime.now().year

def getScheduleInfo():
    scheduleSoup = fetch.fetchSchedule(SEASON_ID)
    leagueName = replace_end(scheduleSoup.title.text,' Schedule -  ESPN', '')
    print( "Beginning parse of %s's %s season..." % (leagueName, SEASON_ID) )

    schedule = dict()
    rows = scheduleSoup.find_all('a', href=True)
    for r in rows:
        if 'boxscorequick' in r['href']:
            teamId = ''
            scoringPeriodId = ''
            vals = r['href'].split('&')
            for val in vals:
                if 'teamId' in val:
                    teamId = val.replace('teamId=', '')
                elif 'scoringPeriodId' in val:
                    scoringPeriodId = val.replace('scoringPeriodId=', '')
                    break
            if scoringPeriodId in schedule:
                schedule[scoringPeriodId].append(teamId)
            else:
                schedule[scoringPeriodId] = [teamId]
    return schedule, leagueName

def getScoreInfo( scoreSoup ):
    d = dict()
    currentIndex = 0
    totalScores = scoreSoup.find_all('div', class_='totalScore')
    benchScores = scoreSoup.select('div[id*="tmInactivePts"]')
    teamNames = scoreSoup.find_all('tr', class_='playertableTableHeader')
    for team in teamNames:
        teamName = team.text.replace(' Box Score', '')
        d[teamName] = dict()
        actualPoints = Decimal(totalScores[currentIndex]['title'])
        benchPoints = Decimal(benchScores[currentIndex].text if len(benchScores) > 0 else 0)
        d[teamName]['actualPoints'] = float(actualPoints)
        d[teamName]['benchPoints'] = float(benchPoints)
        d[teamName]['totalPoints'] = float(actualPoints + benchPoints)
        currentIndex += 1
    return d

def parseLeagueResults( weeks ):
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

def printResults( leagueName, leagueResults ):
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