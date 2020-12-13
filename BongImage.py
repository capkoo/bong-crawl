import sys

import openpyxl
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
                             QProgressBar, QFileDialog, QTableWidget, QTableWidgetItem, QListWidget)


class BongImageDownloaderUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()

        self.openFileBtn = QPushButton('&Open Excel')
        self.lineFilePath = QLineEdit('')
        self.startButton = QPushButton('&Start')
        self.progressbar = QProgressBar()
        self.textResult = QTextEdit()
        self.tableWidget = QTableWidget()
        self.listWidget = QListWidget()


        self.openFileBtn.clicked.connect(self.showFileDialog)
        self.lineFilePath.setReadOnly(True)
        self.startButton.setDisabled(True)
        self.progressbar.setValue(0)

        self.grid.addWidget(self.openFileBtn, 0, 0)
        self.grid.addWidget(self.lineFilePath, 0, 1)
        self.grid.addWidget(self.startButton, 1, 0, 1, 4)
        self.grid.addWidget(self.progressbar,2 , 0, 1, 4)
        self.grid.addWidget(self.tableWidget, 3, 0, 1, 4)

        self.setLayout(self.grid)


        self.setWindowTitle('Bong Image Downloader')
        self.setGeometry(300, 100, 400, 600)
        self.show()

    def showFileDialog(self):
        fileDialog = QFileDialog()
        fname = fileDialog.getOpenFileName(self, 'Open file', './' ,"Excel Files (*.xls *.xlsx)")
        self.excelFilePath = fname[0]
        self.lineFilePath.setText(self.excelFilePath)
        self.startButton.setDisabled(False)
        try:
            self.setTableItem()
        except Exception as e:
            print(e)


    def setTableItem(self):
        wb = openpyxl.load_workbook(self.excelFilePath, read_only=True)
        ws = wb.active
        # print(ws.rows[0])

        # headers = [item.value for item in ws if item.value is not None]


        headerCells = ws['A1':'N1']
        print(headerCells)

        headers = []
        for row in headerCells:
            for cell in row:
                headers.append(cell.value)

        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        data = ws.iter_rows()
        next(data)

        for x, rows in enumerate(data):
            print(rows)
            if rows[0].value is not None:
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                for y, cell in enumerate(rows):
                    val = cell.value
                    if val is not None:
                        item = QTableWidgetItem(str(val))
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        self.tableWidget.setItem(self.tableWidget.rowCount() - 1, y, item)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BongImageDownloaderUI()
    sys.exit(app.exec_())