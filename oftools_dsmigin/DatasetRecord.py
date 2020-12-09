class RecordColumn:
    DSN = 0
    COPYBOOK = 1
    RECFM = 2
    LRECL = 3
    BLKSIZE = 4
    DSORG   = 5
    VOLSER  = 6
    VSAM    = 7
    KEYOFF  = 8
    KEYLEN  = 9
    MAXLRECL =10
    AVGLRECL = 11
    CISIZE = 12
    IGNORE  = 13
    FTP = 14
    FTPDATE = 15
    FTPTIME = 16
    DSMIGIN = 17
    DSMIGINDATE = 18
    DSMIGINTIME = 19

    nameList = ['DSN', 'COPYBOOK', 'RECFM', 'LRECL', 'BLKSIZE', 'DSORG', 'VOLSER', 'VSAM',
                'KEYOFF', 'KEYLEN', 'MAXLRECL', 'AVGLRECL', 'CISIZE', 'IGNORE', 'FTP', 'FTPDATE',
                'FTPTIME', 'DSMIGIN', 'DSMIGINDATE', 'DSMIGINTIME']

class DatasetRecord:
    def __init__(self):

        self.cols = []
        i = 0
        while i < len(RecordColumn.nameList):
            self.cols.append("")
            i = i+1

    def printRecord(self):
        for i in range(len(self.cols)):
            print(self.cols[i]) 

    def setColumns(self, cols):
        for i in range(len(cols)):
            self.cols[i] = cols[i].replace(" ","")

    def getColumns(self):
        return self.cols

    def checkHeader(self, cols):
        error = 0

        if len(cols) != len(RecordColumn.nameList):
            error = 1

        for i in range(len(cols)):
            if cmp(cols[i].strip(), RecordColumn.nameList[i].strip()) != 0:
               error = 1
               break

        if error != 0:
           print("Columns does not match with the program")                
           print("input file:")
           print(cols)
           print("program definition:")
           print (RecordColumn.nameList)
           exit(-1)
      
    def setDirInfo(self, info):
        infoList = info.split()

        # Migrated
        if cmp("Migrated", infoList[0]) == 0:
            self.cols[RecordColumn.VOLSER] = infoList[0]
            if (len(self.cols[RecordColumn.VOLSER]) < 1):
                return
            return

        # Pseudo directoy
        if cmp("Pseudo", infoList[0]) == 0:
            if (len(self.cols[RecordColumn.VOLSER]) < 1):
                self.cols[RecordColumn.VOLSER] = infoList[0]
                return
            return

        # VSAM data does not have VOLSER information
        if cmp("VSAM", infoList[0]) == 0:
            self.cols[RecordColumn.DSORG] = infoList[0]
            return

        # VSAM INDEX & DATA only have 4 columns
        if (len(infoList) == 4):
            if cmp("VSAM", infoList[2]) == 0:
                if infoList[3].endswith("INDEX") or infoList[3].endswith("DATA"):
                    self.cols[RecordColumn.VOLSER] = infoList[0]
                    #UNIT = infoList[1]
                    self.cols[RecordColumn.RECFM] = infoList[2]
                    #DSN = infoList[3]
                    return
       
        # Everything else.. 
        self.cols[RecordColumn.VOLSER] = infoList[0]
        if (len(infoList) >= 9):
            #UNIT = infoList[1]
            #REFERRED = infoList[2]
            #EXT = infoList[3]
            #USED = infoList[4]
            #self.cols[RecordColumn.RECFM] = infoList[5]
            #self.cols[RecordColumn.LRECL] = infoList[6]
            #self.cols[RecordColumn.BLKSIZE] = infoList[7]
            #self.cols[RecordColumn.DSORG] = infoList[8]
            #DSN = infoList[9]

            self.cols[RecordColumn.RECFM] = info[33:38].strip()
            self.cols[RecordColumn.LRECL] = info[39:44].strip()
            self.cols[RecordColumn.BLKSIZE] = info[45:50].strip()
            self.cols[RecordColumn.DSORG] = info[51:55].strip()
           
        return 
 
