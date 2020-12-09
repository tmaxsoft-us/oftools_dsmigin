from DatasetRecord import DatasetRecord
from DatasetRecord import RecordColumn
import os
import io
import subprocess

class DsmiginHandler:
#TODO add functionality to record time
    def __init__(self):
        return

    def dsmigin(self,row,opt):
#        if cmp(row.cols[RecordColumn.DSORG], "VSAM") == 0:
#            if updateDatasetInfo(row) < 0:
#                return -1

        rc = self.cobgensch(row.cols[RecordColumn.COPYBOOK])
        if rc < 0:
            return rc

        if cmp(row.cols[RecordColumn.DSORG], "PS") == 0:
            return self.dsmiginPS(row,opt)
        elif cmp(row.cols[RecordColumn.DSORG], "PO") == 0:
            return self.dsmiginPO(row,opt)
        elif cmp(row.cols[RecordColumn.DSORG], "VSAM") == 0:
            return self.dsmiginVSAM(row,opt)
        else:
            print(row.cols[RecordColumn.DSORG])
            pass
        return 0

    def dsmiginPS(self,row,opt):
        if "C" in row.cols[RecordColumn.DSMIGIN]:
            return -1

        command = 'dsdelete '
        command += row.cols[RecordColumn.DSN] 
        command = self.finalizeCommand(command)
        print(command)
        p = subprocess.Popen([command], stdin=subprocess.PIPE, shell=True)
        p.communicate(input=b' '+command)[0]

        command = 'dsmigin '
        #command += opt.work + '/'
        command += row.cols[RecordColumn.DSN] + ' ' 
        command += row.cols[RecordColumn.DSN] 
        command += ' -s ' + row.cols[RecordColumn.COPYBOOK].split('.')[0] + '.conv'

        #if cmp("FBA", row.cols[RecordColumn.RECFM]) == 0:
        #    command += ' -f FB'
        #else:
        #    command += ' -f ' + row.cols[RecordColumn.RECFM] 

        command += ' -f ' + row.cols[RecordColumn.RECFM] 
        command += ' -l ' + row.cols[RecordColumn.LRECL]
        command += ' -b ' + row.cols[RecordColumn.BLKSIZE]
        command += ' -o ' + row.cols[RecordColumn.DSORG]
        if "C" in row.cols[RecordColumn.DSMIGIN]:
            command += ' -C '
        if "F" in row.cols[RecordColumn.DSMIGIN]:
            command += " -F "
        command += ' -sosi 6 '
        command = self.finalizeCommand(command)
        print(command)
        p = subprocess.Popen([command], stdin=subprocess.PIPE, shell=True)
        p.communicate(input=b' '+command)[0]
        return p.returncode

    def dsmiginPO(self,row,opt):
    #Add subprocess to cd into PDS, then store members in a list
    #dsmigin with dsn and member list
    # https://stackoverflow.com/questions/11968976/list-files-only-in-the-current-directory
        rc = 0

        if "C" in row.cols[RecordColumn.DSMIGIN]:
            cwd = os.getcwd()
            work_dir = cwd + '/' + row.cols[RecordColumn.DSN]
            convert_dir = cwd + '_convert/' + row.cols[RecordColumn.DSN]

            try:
                os.makedirs(convert_dir)
            except OSError as error:
                print("dir already exist... skipping mkdir")

            for member in os.listdir(work_dir):
                command = 'dsmigin '
                command += work_dir + '/' + member + ' '
                command += convert_dir + '/' + member + ' '
                command += ' -s ' + row.cols[RecordColumn.COPYBOOK].split('.')[0] + '.conv'
                command += ' -o PS '
                command += ' -l ' + row.cols[RecordColumn.LRECL]
                command += ' -b ' + row.cols[RecordColumn.BLKSIZE]
                command += ' -f L ' 
                command += " -C "
                command += ' -sosi 6 '
                command = self.finalizeCommand(command)
                print(command)
                p = subprocess.Popen([command], stdin=subprocess.PIPE, shell=True)
                p.communicate(input=b' '+command)[0]
                rc = p.returncode
                if rc != 0:
                    return rc
        else:
            command = 'dsdelete '
            command += row.cols[RecordColumn.DSN] 
            command = self.finalizeCommand(command)
            print(command)
            p = subprocess.Popen([command], stdin=subprocess.PIPE, shell=True)
            p.communicate(input=b' '+command)[0]

            if row.cols[RecordColumn.DSN] is not None:
                command = 'dscreate '
                command += row.cols[RecordColumn.DSN]
                command += ' -o PO '
                command += ' -l ' + row.cols[RecordColumn.LRECL]
                command += ' -b ' + row.cols[RecordColumn.BLKSIZE]
           
                if 'F' in row.cols[RecordColumn.RECFM] and cmp("PO", row.cols[RecordColumn.DSORG]) == 0 and cmp("80", row.cols[RecordColumn.LRECL]) == 0 and cmp("L_80.convcpy", row.cols[RecordColumn.COPYBOOK]) == 0:
                    command += ' -f L ' 
                else:
                    command += ' -f ' + row.cols[RecordColumn.RECFM] 

                command = self.finalizeCommand(command)
                print(command)
                p = subprocess.Popen([command], stdin=subprocess.PIPE, shell=True)
                p.communicate(input=b' '+command)[0]

            cwd = os.getcwd()
            os.chdir(cwd + '/' +  row.cols[RecordColumn.DSN])
            newcwd = os.getcwd()
            memList = os.listdir(newcwd)

            for member in os.listdir(newcwd):
                command = 'dsmigin '
                command += member + ' '
                command += row.cols[RecordColumn.DSN]
                command += ' -m ' + member
                command += ' -s ' + row.cols[RecordColumn.COPYBOOK].split('.')[0] + '.conv'
                command += ' -o ' + row.cols[RecordColumn.DSORG]
                command += ' -l ' + row.cols[RecordColumn.LRECL]
                command += ' -b ' + row.cols[RecordColumn.BLKSIZE]

                if 'F' in row.cols[RecordColumn.RECFM] and cmp("PO", row.cols[RecordColumn.DSORG]) == 0 and cmp("80", row.cols[RecordColumn.LRECL]) == 0 and cmp("L_80.convcpy", row.cols[RecordColumn.COPYBOOK]) == 0:
                    command += ' -f L ' 
            #bug in dsmigin... FBA is not allowed for PO dataset
            #elif cmp("FBA", row.cols[RecordColumn.RECFM]) == 0:
            #    command += ' -f FB'
                else:
                    command += ' -f ' + row.cols[RecordColumn.RECFM] 

                if "C" in row.cols[RecordColumn.DSMIGIN]:
                    #dsmigin bug for -C option
                    command += " -C "

                    #just try dsmiginPS for -C option
                    command = 'dsmigin '
                    command += member + ' '
                    command += ' -s ' + row.cols[RecordColumn.COPYBOOK].split('.')[0] + '.conv'
                    command += ' -o PS '
                    command += ' -l ' + row.cols[RecordColumn.LRECL]
                    command += ' -b ' + row.cols[RecordColumn.BLKSIZE]
                    command += ' -f ' + row.cols[RecordColumn.RECFM] 
                    command += " -C "
                if "F" in row.cols[RecordColumn.DSMIGIN]:
                    command += " -F "
                command += ' -sosi 6 '
                command = self.finalizeCommand(command)
                print(command)
                p = subprocess.Popen([command], stdin=subprocess.PIPE, shell=True)
                p.communicate(input=b' '+command)[0]
                rc = p.returncode
                if rc != 0:
                    os.chdir(cwd)
                    return rc             
            os.chdir(cwd)

        return rc
    
    def dsmiginVSAM(self, row, opt):
        command = 'idcams delete -t CL '
        command += ' -n ' + row.cols[RecordColumn.DSN]
        command = self.finalizeCommand(command)
        print(command)
        p = subprocess.Popen([command], stdin=subprocess.PIPE, shell=True)
        p.communicate(input=b' '+command)[0]

        command = 'idcams define -t CL '
        command += ' -o ' + row.cols[RecordColumn.VSAM]
        command += ' -l ' + row.cols[RecordColumn.AVGLRECL] + ',' + row.cols[RecordColumn.MAXLRECL]
        command += ' -k ' + row.cols[RecordColumn.KEYLEN] + ',' + row.cols[RecordColumn.KEYOFF]
        command += ' -n ' + row.cols[RecordColumn.DSN]
        command = self.finalizeCommand(command)
        print(command)
        p = subprocess.Popen([command], stdin=subprocess.PIPE, shell=True)
        p.communicate(input=b' '+command)[0]

        command = 'dsmigin '
        #command += opt.work + '/'
        command += row.cols[RecordColumn.DSN] + ' ' 
        command += row.cols[RecordColumn.DSN] 
        command += ' -s ' + row.cols[RecordColumn.COPYBOOK].split('.')[0] + '.conv'
        command += ' -f ' + row.cols[RecordColumn.RECFM]
        command += ' -R '
        command += ' -sosi 6 '
        command = self.finalizeCommand(command)
        print(command)
        p = subprocess.Popen([command], stdin=subprocess.PIPE, shell=True)
        p.communicate(input=b' '+command)[0]
        if p.returncode != 0:
            return p.returncode

        return 0

    def cobgensch(self, copybook):
        command = 'cobgensch ../copybook/'
        command += copybook
        command = self.finalizeCommand(command)
        print(command)
        p = subprocess.Popen([command], stdin=subprocess.PIPE, shell=True)
        p.communicate(input=b' '+command)[0]
        return p.returncode

    def finalizeCommand(self, command):
        command = command.replace("$", "\\$") 
        command = command.replace("#", "\\#") 
        print(command)
        return command 
