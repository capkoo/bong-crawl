import sys
import os
from crawl.iherbCrawl import IherbCrawl

class Main:
    def __init__(self):
        self.setExceptionHandler()
        IherbCrawl().exRun()


    def setExceptionHandler(self):
        # Back up the reference to the exceptionhook
        sys._excepthook = sys.excepthook

        # Set the exception hook to our wrapping function
        sys.excepthook = self.myExceptionHandler


    def myExceptionHandler(exctype, value, traceback):
        # Print the error and traceback
        print(exctype, value, traceback)
        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)
        os.system("pause")
        # sys.exit(1)

Main()
exit()

try:
    Main()
    os.system("pause")
except Exception as e:
    print(e)
    os.system("pause")
