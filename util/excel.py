from openpyxl import Workbook
import os


class Excel:
    def __init__(self):
        self.workbook = Workbook()
        self.sheet = self.workbook.active


    def setSheetName(self, sheetName):
        self.sheet.title = sheetName



    def appendRow(self, row):
        self.sheet.append(row)
        return


    def save(self, dirPath, fileName):
        os.makedirs(dirPath, exist_ok=True)
        self.workbook.save(dirPath + '/' + fileName)



