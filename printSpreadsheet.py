from os import getenv, makedirs, path

import xlsxwriter as xlsx
from dotenv import load_dotenv

load_dotenv()
SEASON_ID = getenv('SEASON_ID')
RESULT_DIRECTORY = 'results'


class printSpreadsheet:

    def __init__(self, teamInfo:dict, leagueName:str, leagueResults:dict, schedule:dict):
        self.teamInfo = teamInfo
        self.leagueName = leagueName
        self.leagueResults = leagueResults
        self.schedule = schedule
        self.outputFileName = ('%s/%s-%s.xlsx' % (RESULT_DIRECTORY, leagueName.replace(' ', '-'), SEASON_ID))
        self.workbook = xlsx.Workbook(self.outputFileName)

    def printSpreadsheet(self):
        print('Printing to %s...' % (self.outputFileName), end='', flush=True)
        if not path.exists(RESULT_DIRECTORY):
            makedirs(RESULT_DIRECTORY)
        worksheet = self.workbook.add_worksheet('Starter Points')
        worksheet.write('A1', 'Team')
        self.workbook.close()
        print('DONE')
