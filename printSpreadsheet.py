from collections import OrderedDict
from decimal import Decimal
from os import getenv, makedirs, path

import win32com.client as win32
import xlsxwriter as xlsx
from dotenv import load_dotenv
from pydash import shift, slugify

load_dotenv()
SEASON_ID = getenv('SEASON_ID')
RESULT_DIRECTORY = 'results'
POINT_TYPES = ['starter', 'bench', 'total']

class printSpreadsheet:

    def __init__(self, teamInfo:dict, leagueName:str, leagueResults:OrderedDict, schedule:OrderedDict):
        self.teamInfo = teamInfo
        self.leagueName = leagueName
        self.leagueResults = leagueResults
        self.schedule = schedule
        self.outputFileName = ('%s/%s-%s.xlsx' % (RESULT_DIRECTORY, slugify(leagueName), SEASON_ID))
        self.workbook = xlsx.Workbook(self.outputFileName)
        self.centerAlign = self.workbook.add_format({'align': 'center'})
        self.centerAlignBold = self.workbook.add_format({'align': 'center', 'bold': True})
        self.centerAlignedNumber = self.workbook.add_format({'align': 'center', 'num_format': '0.00'})

    def getTeamStats(self, teamId:str, sheetName:str ):
        scores = [self.teamInfo[teamId]]
        for week in self.leagueResults.values():
            gameFound = False
            for game in week:
                if teamId in game:
                    scores.append(game[teamId][sheetName])
                    gameFound = True
            if gameFound == False:
                scores.append(0)
        return scores

    def printSheet(self):
        for sheetName in POINT_TYPES:
            worksheet = self.workbook.add_worksheet('%s Points' % (sheetName.capitalize()))
            worksheet.write(0, 0, 'Team', self.centerAlignBold)
            colIndex = 1
            rowIndex = 1
            for week in self.schedule:
                worksheet.write(0, colIndex, 'Week ' + week, self.centerAlignBold)
                colIndex += 1
            worksheet.write(0, colIndex, 'Total', self.centerAlignBold)
            for teamId in self.teamInfo.keys():
                teamStats = self.getTeamStats(teamId, sheetName)
                worksheet.write(rowIndex, 0, shift(teamStats), self.centerAlign)
                total = 0
                colIndex = 1
                for item in teamStats:
                    worksheet.write_number(rowIndex, colIndex, item, self.centerAlignedNumber)
                    total = total + item
                    colIndex += 1
                cellRange = xlsx.utility.xl_range(rowIndex, 1, rowIndex, colIndex - 1)
                formula = '=SUM(%s)' % cellRange
                worksheet.write_formula(rowIndex, colIndex, formula, self.centerAlignedNumber)
                rowIndex += 1
            worksheet.write(rowIndex, 0, 'Totals', self.centerAlignBold)
            for i in range(1, colIndex+1):
                cellRange = xlsx.utility.xl_range(1, i, rowIndex - 1, i)
                formula = '=SUM(%s)' % cellRange
                worksheet.write_formula(rowIndex, i, formula, self.centerAlignedNumber)

    def autoFitSpreadsheet(self):
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        dir_path = path.dirname(path.realpath(__file__))
        wb = excel.Workbooks.Open(dir_path + '/' + self.outputFileName)
        for sheet in wb.Sheets:
            ws = wb.Worksheets(sheet.Name)
            ws.Columns(1).AutoFit()
        wb.Save()
        excel.Application.Quit()

    def printSpreadsheet(self):
        print('Printing to %s...' % (self.outputFileName), end='', flush=True)
        if not path.exists(RESULT_DIRECTORY):
            makedirs(RESULT_DIRECTORY)
        self.printSheet()
        self.workbook.close()
        print('DONE')
        print('Autofitting columns...', end='', flush=True)
        self.autoFitSpreadsheet()
        print('DONE')
