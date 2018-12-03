from collections import OrderedDict
from decimal import Decimal
from os import getenv, makedirs, path

import xlsxwriter as xlsx
from dotenv import load_dotenv
from pydash import shift

import win32com.client as win32

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
        self.outputFileName = ('%s/%s-%s.xlsx' % (RESULT_DIRECTORY, leagueName.replace(' ', '-'), SEASON_ID))
        self.workbook = xlsx.Workbook(self.outputFileName)
        self.centerAlign = self.workbook.add_format({'align': 'center'})
        self.centerAlignedNumber = self.workbook.add_format({'align': 'center', 'num_format': '0.00'})

    def getTeamStats(self, teamId:str, sheetName:str ):
        scores = [self.teamInfo[teamId]]
        for week in self.leagueResults.values():
            for game in week:
                if teamId in game:
                    scores.append(game[teamId][sheetName])
                    break
        return scores

    def printSheet(self, sheetName:str):
        worksheet = self.workbook.add_worksheet('%s Points' % (sheetName.capitalize()))
        
        worksheet.write(0, 0, 'Team', self.centerAlign)
        colIndex = 1
        for week in self.schedule:
            worksheet.write(0, colIndex, 'Week ' + week, self.centerAlign)
            colIndex += 1
        worksheet.write(0, colIndex, 'Total', self.centerAlign)
        rowIndex = 1
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
        for sheet in POINT_TYPES:
            self.printSheet(sheet)
        self.workbook.close()
        print('DONE')
        print('Autofitting columns...', end='', flush=True)
        self.autoFitSpreadsheet()
        print('DONE')
