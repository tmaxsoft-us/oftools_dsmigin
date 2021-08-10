#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This modules runs the FTP Job.

    Typical usage example:
      job = DownloadJob()
      job.run()"""

# Generic/Built-in modules
import os
import time

# Third-party modules

# Owned modules
from .Context import Context
from .Job import Job
from .Log import Log
from .MigrationEnum import Col
from .Utils import Utils


class FTPJob(Job):
    """A class used to run the FTP job.

        This class contains a run method that executes all the steps of the job.

        Methods:
            _format_dataset_info(shell_result): Process FTP command output to retrieve useful information and format it.
            _get_mainframe_dataset_info(records): Execute command on mainframe to retrieve dataset info.
            _recall(record): Executes FTP command to make dataset available to download.
            _analyze(record): Assess download eligibility.
            download(records): Main method for dataset download from mainframe to Linux server.
            run(): Perform all the steps to download datasets using FTP and update the CSV file."""

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
        unset_list = ('', ' ', None)
        root_skipping_message = '[ftp] Skipping dataset: ' + record[
            Col.DSN.value] + ': '

        # Dataset organization considerations
        if record[Col.DSORG.value] in ('PS', 'PO'):
            rc = 0

            # Evaluating potential reasons of skipping
            if record[Col.IGNORE.value] == 'Y':
                Log().logger.info(root_skipping_message + 'IGNORE set to "Y"')
                rc = 1
            elif record[Col.FTP.value] == 'N':
                Log().logger.info(root_skipping_message +
                                  'Dataset already successfully downloaded')
                rc = 1
            elif record[Col.FTP.value] in ('', 'Y', 'F'):
                Log().logger.info('')
                rc = 0
            elif record[Col.VOLSER.value] == 'Pseudo':
                Log().logger.info(root_skipping_message +
                                  'VOLSER set to "Pseudo" directory')
                rc = 1
            elif record[Col.VOLSER.value] == 'Migrated':
                Log().logger.info(
                    'VOLSER set to "Migrated" directory. Recalling dataset: ' +
                    record[Col.DSN.value])
                rc = 2

            if rc in (0, 2):
                Log().logger.debug('[ftp] DSORG set to "' +
                                   record[Col.DSORG.value] +
                                   '". Proceeding to download')

        elif record[Col.DSORG.value] == 'VSAM':
            if Context().prefix == '':
                Log().logger.warning(
                    root_skipping_message +
                    'PrefixError: -p or --prefix option must be specified for VSAM dataset download from mainframe'
                )
                rc = 1
            else:
                Log().logger.debug('[ftp] DSORG set to "' +
                                   record[Col.DSORG.value] +
                                   '". Proceeding to download')
                rc = 0

        elif record[Col.DSORG.value] in unset_list:
            Log().logger.warning(
                root_skipping_message +
                'Missing DSORG information for the given dataset')
            rc = 1

        else:
            Log().logger.error(
                root_skipping_message +
                'Invalid DSORG information for the given dataset')
            rc = 1

        return rc

    def _recall(self, record):
        """Executes FTP command to make dataset available to download.

            If a dataset has 'Migrated' as VOLSER parameter, the program executes this recall method just to open the diretory containing the dataset to trigger download execution from the mainframe.

            Args:
                record: A list, the dataset data to execute the recall using the DSN.

            Returns:
                An integer, the return code of the method."""
        ftp_command = 'cd ' + record[Col.DSN.value] + '\nquit\n'
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _download_PS(self, dsn, rdwftp):
        """
            """
        Log().logger.debug('[ftp] Downloading PS dataset: ' + dsn)
        ftp_command = rdwftp + '\nget ' + dsn + '\nquit\nEOF'
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _download_PO(self, dsn, rdwftp):
        """
            """
        Log().logger.debug('[ftp] Downloading PO dataset: ' + dsn)
        # Creating the directory for the PO dataset
        if not os.path.exists(dsn):
            os.makedirs(dsn)
        os.chdir(dsn)
        ftp_command = rdwftp + '\ncd ' + dsn + '\nmget -c *\nquit\nEOF\n'
        _, _, rc = Utils().execute_ftp_command(ftp_command)
        os.chdir(Context().dataset_directory)

        return rc

    def _download_VSAM(self, dsn, rdwftp):
        """
            """
        Log().logger.debug('[ftp] Downloading PS dataset: ' + dsn)
        ftp_command = rdwftp + '\nget ' + Context().prefix + dsn + ' ' + dsn + '\nquit\nEOF'
        _, _, rc = Utils().execute_ftp_command(ftp_command)


        return rc

    def _download(self, record):
        """Main method for dataset download from mainframe to Linux server.

            Args:
                records: A 2D-list, the elements of the CSV file containing all the dataset data.

            Returns:
                A 2D-list, dataset data after all the changes applied in the download execution."""

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
        elif record[Col.DSORG.value] == 'VSAM':
            rc = self._download_VSAM(record[Col.DSN.value], rdwftp)

        elapsed_time = time.time() - start_time

        # Processing the result of the download
        if rc == 0:
            status = 'SUCCESS'
            record[Col.FTPDATE.value] = Context().timestamp
            record[Col.FTPDURATION.value] = str(round(elapsed_time, 4))
            if record[Col.FTP.value] != 'F':
                record[Col.FTP.value] = 'N'
        else:
            status = 'FAILED'

        Log().logger.info('DOWNLOAD ' + status + ' (' +
                          str(round(elapsed_time, 4)) + ' s)')

        return rc

    def run(self, record):
        """Perform all the steps to download datasets using FTP and update the CSV file.

            It first creates a backup of the CSV file and loads it. Then, it executes the FTP command to download datasets and updating the FTP status (success or fail) at the same time. It finally writes the changes to the CSV, and updates the statistics.

            Returns: 
                An integer, the return code of the job."""
        Log().logger.debug('[ftp] Starting Job')
        os.chdir(Context().dataset_directory)
        rc = 0

        # Skipping dataset download under specific conditions
        rc = self._analyze(record)
        if rc == 1:
            return rc
        elif rc == 2:
            self._recall(record)

        rc = self._download(record)
        if rc == 0:
            self._storage_resource.write()
            self._number_downloaded += 1

            if Context().number_datasets != 0:
                Log().logger.info('[ftp] Current dataset download count: ' +
                                  str(self._number_downloaded) + '/' +
                                  str(Context().number_datasets))
                if self._number_downloaded >= Context().number_datasets:
                    Log().logger.info('[ftp] Limit of dataset download reached')
                    rc = 3
            else:
                Log().logger.info('[ftp] Current dataset download count: ' +
                                  str(self._number_downloaded))

        Log().logger.debug('[ftp] Ending Job')

        return rc
