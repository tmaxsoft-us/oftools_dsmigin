import io
import os
import subprocess

class FTPHandler:
    def __init__(self, ip):
        self.ip = ip

    def getInfo(self, dsn):
        commandString = 'lftp -e "cd ..; dir ' + dsn + ';quit;" ' +  self.ip + " "
        #os.system(commandString)
        #result = subprocess.check_output(commandString, shell=True)
        p = subprocess.Popen([commandString], stdout=subprocess.PIPE, shell=True)
        #p.communicate()

        while True:
            line = p.stdout.readline()
            if not line:
                break

            if dsn in line:
                return line

        return None

    def download(self, dsn, dsorg, recfm):
        commandString = ""
        rdwftp = ""

        if recfm[0] is 'V':
            rdwftp = "quote site rdw\n"
#            rdwftp = ""

        if cmp(dsorg, "VSAM") == 0:
            print("VSAM data is not able to download directly")
            return -100

        if cmp(dsorg, "PS") == 0:
            commandString = 'ftp -i ' + self.ip 
            ftpcommand = "\nbianry\n" + rdwftp + "\ncd ..\nbinary\nget " + dsn +"\nquit\n"   

            #commandString = 'lftp -e "' + "" + 'cd ..; get -c ' + dsn + ';quit;" ' +  self.ip + " "
            #p = subprocess.Popen([commandString], stdout=subprocess.PIPE, shell=True)
            #p.communicate()

            p = subprocess.Popen([commandString], subprocess.PIPE, shell=True)
            p.communicate(input=b' '+ftpcommand)[0]

            return p.returncode

        elif cmp(dsorg, "PO") == 0:
            if not os.path.exists(dsn):
                os.makedirs(dsn)

            os.chdir(dsn)

            # do not know why but lftp fails on some PDS data
            #commandString = 'lftp -e "set xfer:clobber yes;cd ../' + dsn + '; mget *;quit;" ' +  self.ip + " "  
            commandString = 'ftp -i ' + self.ip 
            ftpcommand = "\nbianry\n" + rdwftp + "\ncd ..\ncd " + dsn + "\nbinary\nmget -c *\nquit\n"   

            p = subprocess.Popen([commandString], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
            p.communicate(input=b' '+ftpcommand)[0]

            os.chdir("..")
            return p.returncode

        return -1

    def recall(self, dsn):
        commandString = 'ftp -i ' + self.ip 
        ftpcommand = "\nbianry\ncd ..\ncd " + dsn + "\nquit\n"   

        p = subprocess.Popen([commandString], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        p.communicate(input=b' '+ftpcommand)[0]
        return p.returncode

