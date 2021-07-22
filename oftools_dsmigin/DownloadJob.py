#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This modules runs the Download Job.

    Typical usage example:
      job = DownloadJob()
      job.run()"""

# Generic/Built-in modules
import os
import time

# Third-party modules

# Owned modules
from .MigrationEnum import Col
from .Context import Context
from .Job import Job
from .Log import Log
from .Utils import Utils


class DownloadJob(Job):
    """A class used to run the download job.

        This class contains a run method that executes all the steps of the job.

        Methods:
            _format_dataset_info(shell_result): Process FTP command output to retrieve useful information and format it.
            _get_mainframe_dataset_info(records): Execute command on mainframe to retrieve dataset info.
            _recall(record): Executes FTP command to make dataset available to download.
            _analyze(record): Assess download eligibility.
            download(records): Main method for dataset download from mainframe to Linux server.
            run(): Perform all the steps to download datasets using FTP and update the CSV file."""

    def _format_dataset_info(self, ftp_result):
        """Process FTP command output to retrieve useful information and format it.

            Args:
                shell_result: A string, the result of the FTP ls command.
            
            Returns:
                A list, dataset data correctly formatted and organized."""
        line = ftp_result.splitlines()
        fields = line[1].split()
        # Retrieve dataset parameters one by one
        recfm = fields[5]
        lrecl = fields[6]
        blksize = fields[7]
        dsorg = fields[8]
        volser = fields[0]

        return [recfm, lrecl, blksize, dsorg, volser]

    def _get_dataset_info(self, record_index):
        """Execute command on mainframe to retrieve dataset info.

            It executes the ls command for each dataset in the records list to retrieve general info about datasets such as RECFM, LRECL, BLKSIZE, DSORG and VOLSER. It uses the submethod formatting_dataset_info to parse the ftp command output.

            Args:
                records: A 2D-list, the elements of the CSV file containing all the dataset data.

            Returns:
                A 2D-list, the dataset data after update with mainframe information."""
        record = Context().records[record_index].columns
        ftp_command = 'ls ' + record[Col.DSN.value] + '\nquit\nEOF'
        stdout, _, rc = Utils().execute_ftp_command(ftp_command)

        if rc == 0:
            dataset_info = self._format_dataset_info(stdout)

            # Retrieved from the result of the FTP command
            record[Col.RECFM.value] = dataset_info[0]
            record[Col.LRECL.value] = dataset_info[1]
            record[Col.BLKSIZE.value] = dataset_info[2]
            record[Col.DSORG.value] = dataset_info[3]
            record[Col.VOLSER.value] = dataset_info[4]
            #TODO Create VSAM dataset to check if there is always the same number of dataset info

            Context().records[record_index].columns = record
            self._csv.write()
        else:
            Log().logger.info('[FTP] Dataset info retrieval failed')

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
                An integer, the return code of the method."""
        rc = 0
        unset_list = ('', ' ', None)
        root_message = '[FTP] Skipping dataset: ' + record[
            Col.DSN.value] + '. Reason: '

        # Missing information for download execution
        if record[Col.DSORG.value] == 'PO' or record[Col.DSORG.value] == 'PS':
            if record[Col.RECFM.value] in unset_list:
                Log().logger.info(
                    root_message +
                    'missing record format RECFM information for the given dataset.'
                )
                rc = -1
        elif record[Col.DSORG.value] in unset_list:
            Log().logger.info(
                root_message +
                'missing DSORG information for the given dataset.')
            rc = -1

        # Skipping dataset download - FTP set to No
        if record[Col.FTP.value] == 'NO':
            Log().logger.info(root_message + 'FTP flag set to "No".')
            rc = -1
        # Skipping dataset download - Successful, already done
        elif record[Col.FTP.value] == 'SUCCESS':
            Log().logger.info(root_message + 'already successfully downloaded.')
            rc = -1

        # Skipping dataset download - errors, warnings, ignore, specific conditions
        if record[Col.IGNORE.value] == 'YES':
            Log().logger.info(root_message + 'IGNORE flag set to "Yes".')
            rc = -1
        if record[Col.VOLSER.value] == 'Pseudo':
            Log().logger.info(root_message +
                              'VOLSER set to "Pseudo" directory.')
            rc = -1
        # Recalling migrated dataset
        elif record[Col.VOLSER.value] == 'Migrated':
            Log().logger.info(
                'VOLSER set to "Migrated" directory. Recalling dataset: ' +
                record[Col.DSN.value])
            rc = 1

        if record[Col.RECFM.value] == 'U':
            Log().logger.info(root_message +
                              'RECFM set to "U", undefined record format.')
            rc = -1
        if record[Col.DSORG.value] == 'VSAM':
            Log().logger.info(
                root_message +
                'DSORG set to "VSAM".  It is not possible to download VSAM data directly. It needs to be unloaded first.'
            )
            rc = -1

        # Retry dataset download that was previously failed
        if record[Col.FTP.value] == 'FAILED':
            Log().logger.debug(
                '[FTP] Last download failed. Going to try again.')
            rc = 2

        return rc

    def _recall(self, record_index):
        """Executes FTP command to make dataset available to download.

            If a dataset has 'Migrated' as VOLSER parameter, the program executes this recall method just to open the diretory containing the dataset to trigger download execution from the mainframe.

            Args:
                record: A list, the dataset data to execute the recall using the DSN.

            Returns:
                An integer, the return code of the method."""
        record = Context().records[record_index].columns
        ftp_command = 'cd ' + record[Col.DSN.value] + '\nquit\n'
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _download_PS(self, dsn, rdwftp):
        """
            """
        Log().logger.debug('[FTP] Downloading PS dataset: ' + dsn)
        ftp_command = rdwftp + '\nget ' + dsn + '\nquit\nEOF'
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _download_PO(self, dsn, rdwftp):
        """
            """
        Log().logger.debug('[FTP] Downloading PO dataset: ' + dsn)
        # Creating the directory for the PO dataset
        if not os.path.exists(dsn):
            os.makedirs(dsn)
        os.chdir(dsn)
        ftp_command = rdwftp + '\ncd ' + dsn + '\nmget -c *\nquit\nEOF\n'
        _, _, rc = Utils().execute_ftp_command(ftp_command)
        os.chdir(Context().dataset_directory)

        return rc

    def _download(self, record_index):
        """Main method for dataset download from mainframe to Linux server.

            Args:
                records: A 2D-list, the elements of the CSV file containing all the dataset data.

            Returns:
                A 2D-list, dataset data after all the changes applied in the download execution."""
        record = Context().records[record_index].columns

        # quote is an FTP option and RDW is dataset length for the given dataset
        # This conditional statement allow to retrieve record length for V (Variable) or VB (Variable Blocked) for successful download
        if record[Col.RECFM.value][0] == 'V':
            rdwftp = 'quote site rdw\n'
        else:
            rdwftp = ''

        start_time = time.time()

        if record[Col.DSORG.value] == 'PS':
            rc = self._download_PS(record[Col.DSN.value], rdwftp)
        elif record[Col.DSORG.value] == 'PO':
            rc = self._download_PO(record[Col.DSN.value], rdwftp)

        elapsed_time = time.time() - start_time

        # Processing the result of the download
        record[Col.FTPDATE.value] = Context().timestamp
        if rc == 0:
            Log().logger.info('[FTP] Dataset download success: ' +
                              record[Col.DSN.value])
            record[Col.FTP.value] = 'SUCCESS'
            record[Col.FTPDURATION] = str(elapsed_time)
        elif rc < 0:
            Log().logger.info('[FTP] Dataset download failed: ' +
                              record[Col.DSN.value])
            record[Col.FTP.value] = 'FAILED'
            record[Col.FTPDURATION] = str(elapsed_time)

        Context().records[record_index].columns = record
        self._csv.write()

        return rc

    def run(self):
        """Perform all the steps to download datasets using FTP and update the CSV file.

            It first creates a backup of the CSV file and loads it. Then, it executes the FTP command to download datasets and updating the FTP status (success or fail) at the same time. It finally writes the changes to the CSV, and updates the statistics.

            Returns: 
                An integer, the return code of the job."""
        Log().logger.debug('[FTP] Starting Job')

        number_downloaded = 0
        os.chdir(Context().dataset_directory)

        for i in range(len(self._csv.records)):
            rc = self._get_dataset_info(i)
            if rc != 0:
                continue

            if Context().ftp_type == 'D':
                rc = self._analyze(i)
                if rc == 1:
                    self._recall(i)
                elif rc < 0:
                    continue

                rc = self._download(i)
                if rc != 0:
                    continue
                else:
                    number_downloaded += 1

                    if Context().number_datasets != 0:
                        if number_downloaded < Context().number_datasets:
                            Log().logger.info('[FTP] Current download count: ' +
                                              str(number_downloaded) + '/' +
                                              str(Context().number_datasets))
                        else:
                            Log().logger.info(
                                '[FTP] Limit of dataset download reached')
                            break
                    else: 
                        Log().logger.info('[FTP] Current download count: ' +
                                              str(number_downloaded))

        return rc
