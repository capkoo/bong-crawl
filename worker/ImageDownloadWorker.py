import time

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from util.image_downloader import ImageDownloader


class ImageDowloadWorker(QThread):
    def run(self):
        try:
            imageDownloader = ImageDownloader()
            rowCount = 0
            for x, rows in enumerate(self.data):
                if self.check_is_run() != True:
                    return
                rowCount += 1
                productId = rows[1].value
                savePath = self.ui.IMAGE_PATH + '/' + str(productId)
                offset = 8
                for n in range(1, 5):
                    if self.check_is_run() != True:
                        return
                    imageUrl = rows[n+offset].value
                    if imageUrl is not None:
                        # 다운로드 이미지
                        fileName = str(n) + '.jpg'
                        imageDownloader.download(imageUrl, savePath, fileName)
                        QApplication.processEvents()
                        time.sleep(self.ui.delay)

                self.ui.progressbar.setValue(rowCount)

        except Exception as e:
                print(e)

        self.ui.eventDoneDownload()

    def setData(self, data):
        self.data = data


    def setUi(self, ui):
        self.ui = ui


    def stop(self):
        self.isRun = False
        self.quit()
        self.wait(500) #5000ms = 5s

    def check_is_run(self):
        return self.isRun