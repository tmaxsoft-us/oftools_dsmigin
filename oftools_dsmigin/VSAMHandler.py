import os
import csv
import os.path
from os import path

from DatasetRecord import DatasetRecord
from DatasetRecord import RecordColumn

class VSAMHandler:
    def __init__(self):
        return

    def removeDataAndIndex(self, recordList):
        recordDic = {}
        for record in recordList:
            recordDic[record.cols[RecordColumn.DSN]] = record;

        for recordName in recordDic:
            index = recordName+'.INDEX'
            data  = recordName+'.DATA'
            if recordDic.get(index):
                if recordDic.get(data):
                    recordDic.get(recordName).cols[RecordColumn.DSORG] = "VSAM"
                    recordList.remove(recordDic.get(index))
                    recordList.remove(recordDic.get(data))
                    print("remove: " + index)
                    print("remove: " + data)


    def updateDatasetInfo(self, row):
        cwd = os.getcwd()
        os.chdir(os.path.join(cwd,'../listc'))
    
        if path.exists(row.cols[RecordColumn.DSN]) == 0:
            os.chdir(cwd)
            return -1

        with open( row.cols[RecordColumn.DSN] ) as listcfile:
            flag = 0
            for line in listcfile:
                if flag == 1:                         
                    info = line.strip()
                    info = info.replace("-","")
                    infoList = info.split(' ')
                    print(info)
                    for j in range(len(infoList)):
                        if infoList[j].startswith("RKP"):
                            rkp = infoList[j].replace("RKP","")
                            row.cols[RecordColumn.KEYOFF] = rkp
                            print("KEYOFF: " + str(rkp))
                        elif infoList[j].startswith("KEYLEN"):
                            keylen = infoList[j].replace("KEYLEN","")
                            row.cols[RecordColumn.KEYLEN] = keylen
                            print("KEYLEN: " + str(keylen))
                        elif infoList[j].startswith("MAXLRECL"):
                            maxlrecl = infoList[j].replace("MAXLRECL","")
                            row.cols[RecordColumn.MAXLRECL] = maxlrecl
                            print("MAXLRECL: " + str(maxlrecl))
                        elif infoList[j].startswith("AVGLRECL"):
                            avglrecl = infoList[j].replace("AVGLRECL","")
                            row.cols[RecordColumn.AVGLRECL] = avglrecl
                            print("AVGLRECL: " + str(avglrecl))
                        elif infoList[j].startswith("CISIZE"):
                            cisize = infoList[j].replace("CISIZE","")
                            row.cols[RecordColumn.CISIZE] = cisize
                            print("CISIZE: " + str(cisize))
                        elif infoList[j].startswith("INDEXED"):
                            vsam = "KS"
                            row.cols[RecordColumn.VSAM] = vsam
                            print("VSAM: " + vsam)
                if line.find("DATA ------- " + row.cols[RecordColumn.DSN]) >= 0:
                    flag = 1
                    row.cols[RecordColumn.RECFM] = "VB"
                if line.find("INDEX ------ " + row.cols[RecordColumn.DSN]) >= 0:            
                    break      

        os.chdir(cwd)
        listcfile.close()
        return 0
        #if tehre's a listc file on the vsam file we are interested in, open and parse it.
        #update into the recordList
        #This will make sure every field for VSAM is updated
        #If there is no informatio in the csv file, throw an error
