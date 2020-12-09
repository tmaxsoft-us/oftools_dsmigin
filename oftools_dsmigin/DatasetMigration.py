#!/usr/bin/env python
import os
import traceback
import time

from shutil import copyfile
from datetime import datetime
from optparse import OptionParser
from DatasetRecord import DatasetRecord
from DatasetRecord import RecordColumn
from FTPHandler import FTPHandler
from FileHandler import FileHandler
from FileHandler import LogHandler
from VSAMHandler import VSAMHandler
from DsmiginHandler import DsmiginHandler

class DatasetMigration:
    def __init__(self):
        self.cwd = os.getcwd()
        self.csvd = self.cwd + '/csv' 
        self.logd = self.cwd + '/log'
        self.timestr = time.strftime("%Y%d%d_%H%M%S")
        self.logHandler = LogHandler(self.logd + '/dsmigin.out.' + self.timestr)
        self.isPrint = True

    def run(self):
        options = self.processOption()
        fileHandler = FileHandler(self.cwd + '/' + options.inputcsv)

        # Load CSV
        recordList = self.loadCSV(fileHandler)

        # Remove DATA & INDEX for VSAM data
        vsamHandler = VSAMHandler()
        vsamHandler.removeDataAndIndex(recordList)

        # Try FTP & DSMIGIN
        try:
            if options.ftp:
                self.downloadDataset(recordList, int(options.number))
            if options.dsmigin:
                for row in recordList:
                    if row.cols[RecordColumn.DSMIGIN] in ("Y", "C", "F"):
                        if cmp(row.cols[RecordColumn.DSORG], "VSAM") == 0:
                            vsamHandler.updateDatasetInfo(row)

                self.migrateDataset(recordList, options)

        except:
            traceback.print_exc()
            self.logHandler.writeLog("Abort! Saving current status into CSV file", self.isPrint)

        # Save CSV Changes
        self.storeCSV(fileHandler, recordList)   

        # Do a backup
        self.backupCSV(fileHandler, self.csvd, options.inputcsv)   

    def processOption(self):
        parser = OptionParser(usage="usage: %prog [options] filename",
                              version="%prog 1.0")
        parser.add_option("-I", "--inputcsv",
                          action="store", # optional because action defaults to "store"
                          dest="inputcsv",
                          help="[Mandatory] CSV file to use",)
 
        parser.add_option("-N", "--number",
                          action="store", # optional because action defaults to "store"
                          dest="number",
                          help="[Mandatory] number of datasets to be handled",
                          metavar="INTEGER")

        parser.add_option("-F", "--ftp",
                          action="store", # optional because action defaults to "store"
                          dest="ftp",
                          help="[Optional] Y: trigger ftp",
                          metavar="FLAG")

        parser.add_option("-D", "--dsmigin",
                          action="store", # optional because action defaults to "store"
                          dest="dsmigin",
                          help="[Optional] Y: convert & dataset gen, C: trigger convert only",
                          metavar="FLAG")

        parser.add_option("-W", "--work-directory",
                          action="store", # optional because action defaults to "store"
                          dest="work",
                          help="[Mandatory] work directory for ftp download & dsmigin",
                          metavar="DIRECTORY")

#        parser.add_option("-L", "--log-directory",
#                          action="store", # optional because action defaults to "store"
#                          dest="log",
#                          help="[Optional] specify log directory",
#                          metavar="DIRECTORY")

#        parser.add_option("-B", "--backup-directory",
#                          action="store", # optional because action defaults to "store"
#                          dest="backup",
#                          help="[Optional] specify backup directory for csv file",
#                          metavar="DIRECTORY")

        (options, args) = parser.parse_args()
        self.logHandler.writeLog("options:" + str(options), self.isPrint)

        ## handler erros ##
        if options.inputcsv is None:
            print("Error: -I or --inputcsv is missing")
            exit(-1)
        if options.work is None:
            print("Error: -W or --work-directory is missing")
            exit(-1)
        if options.number is None and options.ftp is "Y":
            print("Error: -N or --number is missing")
            exit(-1)
        #if options.dsmigin:
            #print("-D or --dsmigin option is not supported yet")
            #exit(-1)

        if options.number:
            try:
                int(options.number)
            except:
                print("Error: -N or --number is not numeric")
                exit(-1)
        if options.work:
            try:
                os.chdir(options.work)
            except:
                print("Error: -W or --work-directory not accessable for " + options.work )
                exit(-1)

        ## handle non-errors ##

        return options

    def migrateDataset(self, recordList, opt):
        dsmiginObj = DsmiginHandler()

        for row in recordList:
            if row.cols[RecordColumn.DSMIGIN] in ("Y", "C", "F"):
                startTime = time.time()
                returncode = dsmiginObj.dsmigin(row, opt)
                elapsedTime = time.time() - startTime

                if returncode == 0:
                    if row.cols[RecordColumn.DSMIGIN] in ("Y", "C"):
                        row.cols[RecordColumn.DSMIGIN] = "N"

                    row.cols[RecordColumn.DSMIGINTIME] = elapsedTime
                    row.cols[RecordColumn.DSMIGINDATE] = datetime.today().strftime('%Y-%m-%d')
                else:
                    print("migrateDataset RC = "+ str(returncode))
                    exit(returncode)

    def downloadDataset(self, recordList, number):
        numberDownloaded = 0
        ftpHandler = FTPHandler('')

        for row in recordList:
            if numberDownloaded >= number:
                break

            if cmp(row.cols[RecordColumn.IGNORE], "Y") == 0:
               #print("IGNORE: " + row.cols[RecordColumn.DSN])
               continue

            if cmp(row.cols[RecordColumn.FTP], "N") == 0:
               #print("FTP: " + row.cols[RecordColumn.DSN])
               continue

            info = None
            info = ftpHandler.getInfo(row.cols[RecordColumn.DSN])
            if info:
                row.setDirInfo(info)

            # Recalling migrated data
            if cmp("Migrated", row.cols[RecordColumn.VOLSER]) == 0:
                self.logHandler.writeLog("Recalling Migrated Data: " + row.cols[RecordColumn.DSN], self.isPrint)
                #print("Recalling Migrated Data: " + row.cols[RecordColumn.DSN])
                ftpHandler.recall(row.cols[RecordColumn.DSN])

                info = None
                info = ftpHandler.getInfo(row.cols[RecordColumn.DSN])
                if info:
                    row.setDirInfo(info)
           
            if cmp(row.cols[RecordColumn.VOLSER], "Migrated") == 0:
                self.logHandler.writeLog("Skipping Migrated Data: " + row.cols[RecordColumn.DSN], self.isPrint)
                continue
            if cmp(row.cols[RecordColumn.RECFM], "U") == 0:
                self.logHandler.writeLog("Skipping RECFM=U Data: " + row.cols[RecordColumn.DSN], self.isPrint)
                continue
            if cmp(row.cols[RecordColumn.VOLSER], "Pseudo") == 0:
                self.logHandler.wirteLog("Skipping Pseudo directory: " +  row.cols[RecordColumn.DSN], self.isPrint)

            print("Downloading Data: " + row.cols[RecordColumn.DSN])
            startTime = time.time()
            returncode = ftpHandler.download(row.cols[RecordColumn.DSN], row.cols[RecordColumn.DSORG], row.cols[RecordColumn.RECFM])
            elapsedTime = time.time() - startTime
    
            if returncode == 0:
                if cmp(row.cols[RecordColumn.FTP], "F") != 0:
                    row.cols[RecordColumn.FTP] = "N"
                row.cols[RecordColumn.FTPDATE] = datetime.today().strftime('%Y-%m-%d')
                row.cols[RecordColumn.FTPTIME] = str(elapsedTime)
            elif returncode == 1:
                self.logHandler.writeLog("Already Downloaded: " + row.cols[RecordColumn.DSN], self.isPrint)
                continue
            else:
                self.logHandler.writeLog("Download failed: " + row.cols[RecordColumn.DSN], self.isPrint)
                continue

            numberDownloaded = numberDownloaded + 1
            self.logHandler.writeLog("Downloaded Dataset: " + row.cols[RecordColumn.DSN] + ' ' + str(numberDownloaded) + '/' + str(number), self.isPrint)

        self.logHandler.writeLog("Total Downloaded Dataset: " + str(numberDownloaded) + "/" + str(number), self.isPrint)
    def loadCSV(self, fileHandler):
        recordList = fileHandler.readRecordList()
        return recordList

    def storeCSV(self, fileHandler, recordList):
        fileHandler.writeRecordList(recordList)

    def backupCSV(self, fileHandler, csvd, inputcsv):
        if not os.path.exists(csvd): 
            os.makedirs(csvd)

        copyfile(fileHandler.getFilename(), csvd + '/' + inputcsv + '.' + self.timestr)
