#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Module that contains all functions required to communicate, get information and download datasets from the mainframe.

Typical usage example:

  ftp = FTPHandler()
  ftp.get_mainframe_dataset_info(records)
  ftp.download(records)
"""

# Generic/Built-in modules
import os
import subprocess
import time

# Third-party modules

# Owned modules
from .Context import Context
from .MigrationEnum import Col
from .Utils import Utils


class FTPHandler():
    """A class used to perform all task regarding FTP and interactions with the mainframe.

    Attributes:
        _number: An integer, the number of datasets to download in the current execution of oftools_dsmigin.
        _ip_address: A string, the ip address of the mainframe to connect to for the FTP execution.
        _today_date: A string, the date of today respecting a certain format.
        _work_directory: A string, working directory for the program execution.
        _download_directory: A string, located under the working directory, this directory contains all downloaded datasets.
        _records: A 2D-list, the elements of the CSV file containing all the dataset data.

    Methods:
        __init__(): Initializes all attributes.
        get_mainframe_dataset_info(records): Execute command on mainframe to retrieve dataset info.
        _formatting_dataset_info(shell_result): Process FTP command output to retrieve useful information and format it.
        _recall(record): Executes FTP command to make dataset available to download.
        _analyze(record): Assess download eligibility.
        download(records): Main method for dataset download from mainframe to Linux server.
    """

    def __init__(self):
        """Initializes all attributes.
        """
        self._number = Context().get_number()
        self._today_date = Context().get_today_date()
        self._work_directory = Context().get_work_directory()
        self._download_directory = Context().get_dataset_directory()

        self._records = []

    def get_mainframe_dataset_info(self, records):
        """Execute command on mainframe to retrieve dataset info.

        It execcutes the ls command for each dataset in the records list to retrieve general info about datasets such as RECFM, LRECL, BLKSIZE, DSORG and VOLSER. It uses the submethod formatting_dataset_info to parse the ftp command output.

        Args:
            records: A 2D-list, the elements of the CSV file containing all the dataset data.

        Returns:
            A 2D-list, the dataset data after update with mainframe information.
        """
        for record in records:

            ftp_command = 'ls ' + record[Col.DSN.value] + '\nquit\nEOF'
            proc = Utils().execute_ftp_command(ftp_command)

            if proc != None:
                ftp_result = proc.stdout.decode('utf-8')
                dataset_info = self._formatting_dataset_info(ftp_result)

                updated_record = [' ' for element in range(len(Col))]
                # Retrieved from the previous record
                updated_record[Col.DSN.value] = record[Col.DSN.value]
                # Retrieved from the result of the FTP command
                updated_record[Col.RECFM.value] = dataset_info[0]
                updated_record[Col.LRECL.value] = dataset_info[1]
                updated_record[Col.BLKSIZE.value] = dataset_info[2]
                updated_record[Col.DSORG.value] = dataset_info[3]
                updated_record[Col.VOLSER.value] = dataset_info[4]
                # TODO Create VSAM dataset to check if there is always the same number of dataset info

                self._records.append(updated_record)

        return self._records

    def _formatting_dataset_info(self, shell_result):
        """Process FTP command output to retrieve useful information and format it.

        Args:
            shell_result: A string, the result of the FTP ls command.
        
        Returns:
            A list, dataset data correctly formatted and organized.
        """
        dataset_info = []
        line = shell_result.splitlines()
        fields = line[1].split()

        recfm = fields[5]
        lrecl = fields[6]
        blksize = fields[7]
        dsorg = fields[8]
        volser = fields[0]

        # Add everything to the dataset info
        dataset_info.append(recfm, lrecl, blksize, dsorg, volser)

        return dataset_info

    def _recall(self, record):
        """Executes FTP command to make dataset available to download.

        If a dataset has 'Migrated' as VOLSER parameter, the program executes this recall method just to open the diretory containing the dataset to trigger download execution from the mainframe.

        Args:
            record: A list, the dataset data to execute the recall using the DSN.

        Returns:
            An integer, the return code of the method.
        """
        rc = 0
        ftp_command = 'cd ' + record[Col.DSN.value] + '\nquit\n'
        proc = Utils().execute_ftp_command(ftp_command)

        if proc != None:
            rc = proc.returncode
        else:
            rc = -1

        return rc

    def _analyze(self, record):
        """Assess download eligibility. 

        This method double check multiple parameters in the CSV file to make sure that dataset download can process without error:
            - check missing information
            - check FTP and IGNORE columns status
            - check VOLSER column status, trigger recall method
            - check RECFM and DSORG column status

        Args:
            record: A list, the dataset data to execute verification prior download.
        
        Returns:
            An integer, the return code of the method.
        """
        rc = 0
        unset_list = ('', ' ', None)
        message = 'Skipping dataset: ' + record[Col.DSN.value] + '. Reason: '

        # Missing information for download execution
        if record[Col.DSORG.value] == 'PO' or record[Col.DSORG.value] == 'PS':
            if record[Col.RECFM.value] in unset_list:
                print(
                    message +
                    'missing record format RECFM information for the given dataset.'
                )
                rc = -1
        elif record[Col.DSORG.value] in unset_list:
            print(message + 'missing DSORG information for the given dataset.')
            rc = -1

        # Skipping dataset download - FTP set to No
        if record[Col.FTP.value] == 'N':
            print(message + 'FTP flag set to "No".')
            rc = -1
        # Skipping dataset download - Successful, already done
        elif record[Col.FTP.value] == 'S':
            print(message + 'already successfully downloaded.')
            rc = -1

        # Skipping dataset download - errors, warnings, ignore, specific conditions
        if record[Col.IGNORE.value] == 'Y':
            print(message + 'IGNORE flag set to "Yes".')
            rc = -1
        if record[Col.VOLSER.value] == 'Pseudo':
            print(message + 'VOLSER set to "Pseudo" directory.')
            rc = -1
        # Recalling migrated dataset
        elif record[Col.VOLSER.value] == 'Migrated':
            print('VOLSER set to "Migrated" directory. Recalling dataset: ' + record[Col.DSN.value])
            rc = 1
        
        if record[Col.RECFM.value] == 'U':
            print(message + 'RECFM set to "U", undefined record format.')
            rc = -1
        if record[Col.DSORG.value] == 'VSAM':
            print(
                message +
                'DSORG set to "VSAM".  It is not possible to download VSAM data directly. It needs to be unloaded first.'
            )
            rc = -1

        return rc

    def download(self, records):
        """Main method for dataset download from mainframe to Linux server.

        Args:
            records: A 2D-list, the elements of the CSV file containing all the dataset data.

        Returns:
            A 2D-list, dataset data after all the changes applied in the download execution. 
        """
        os.chdir(self._download_directory)
        self._records = records
        number_downloaded = 0
        rc = 0

        for record in self._records:

            dsn = record[Col.DSN.value]
            dsorg = record[Col.DSORG.value]

            # Skipping dataset download under specific conditions
            rc = self._analyze(record)
            if rc <= 0:
                continue
            # Recalling migrated dataset
            elif rc == 1:
                self._recall(record)

            # Stop download process if number is reached
            if number_downloaded >= self._number:
                break

            # Retry dataset download that was previously failed
            if record[Col.FTP.value] == 'F':
                print('Last download failed. Going to try again.')

            # quote is an FTP option and RDW is dataset length for the given dataset
            # This conditional statement allow to retrieve record length for V (Variable) or VB (Variable Blocked) for successful migration
            if record[Col.RECFM.value][0] == 'V':
                rdwftp = 'quote site rdw\n'
            else:
                rdwftp = ''

            start_time = 0.0
            proc = None
            if dsorg == 'PS':
                print('Downloading PS dataset: ' + dsn)
                ftp_command = rdwftp + '\nget ' + dsn + '\nquit\nEOF'

                start_time = time.time()
                proc = Utils().execute_ftp_command(ftp_command)
            elif dsorg == 'PO':
                print('Downloading PO dataset: ' + dsn)
                # Creating the directory for the PO dataset
                if not os.path.exists(dsn):
                    os.makedirs(dsn)
                os.chdir(dsn)
                ftp_command = rdwftp + '\ncd ' + dsn + '\nmget -c *\nquit\nEOF\n'
                start_time = time.time()
                proc = Utils().execute_ftp_command(ftp_command)
                os.chdir(self._download_directory)

            # Process download elapsed time and retrieving return code
            elapsed_time = time.time() - start_time
            if proc != None:
                rc = proc.returncode
            else:
                rc = -1

            # Processing the result of the download
            record[Col.FTPDATE.value] = self._today_date
            if rc == 0:
                print('Dataset download success!')
                record[Col.FTP.value] = 'S'
                record[Col.FTPDURATION] = str(elapsed_time)
            elif rc < 0:
                print('Dataset download failed!')
                record[Col.FTP.value] = 'F'
                continue

            number_downloaded += 1
            print('Downloaded dataset: ' + dsn + '\nCurrent count: ' +
                  str(number_downloaded) + '/' + str(self._number))

        return self._records
