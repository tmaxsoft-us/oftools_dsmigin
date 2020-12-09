import csv

from DatasetRecord import DatasetRecord
from DatasetRecord import RecordColumn

class LogHandler:
    def __init__(self, filename):
        self.filename = filename
        self.fd=open(filename, "w")

    def __del__(self):
        self.fd.close()

    def writeLog(self, message, isPrint):
        if isPrint is True:
            print(message)
        self.fd.write(message+'\n')      
        self.fd.flush()

class FileHandler:
    """
    """

    def __init__(self, filename):
        """
        """
        self.filename = filename

    def readRecordList(self):
        """
        """
        recordList = []
        with open(self.filename) as csvfile:        
            i = 0
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                datasetRecord = DatasetRecord()
                if cmp(row[0].strip(), RecordColumn.nameList[0].strip()) == 0:
                    datasetRecord.checkHeader(row)
                    continue

                datasetRecord.setColumns(row)
                recordList.append(datasetRecord)

        return recordList

    def writeRecordList(self, recordList):
        """
        """
        with open(self.filename, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(RecordColumn.nameList)

            for i in range(len(recordList)):
                spamwriter.writerow(recordList[i].getColumns())
                
    def getFilename(self):
        """
        """
        return self.filename

