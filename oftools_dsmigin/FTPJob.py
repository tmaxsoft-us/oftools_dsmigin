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
        Log().logger.debug('[ftp] Assessing dataset eligibility: ' +
                           record[Col.DSN.value])
        rc = 0

        unset_list = ('', ' ')
        skip_message = '[ftp] Skipping dataset: ' + record[Col.DSN.value] + ': '

        if record[Col.IGNORE.value] == 'Y':
            Log().logger.info(skip_message + 'IGNORE set to "Y"')
            rc = 1
        elif record[Col.LISTCATDATE.value] == '':
            Log().logger.debug(skip_message + 'LISTCATDATE not set')
            rc = 1
        elif record[Col.FTP.value] == 'N':
            Log().logger.debug(skip_message + 'FTP set to "N"')
            rc = 1
        elif record[Col.FTP.value] in ('', 'Y', 'F'):
            Log().logger.debug('[ftp] FTP set to "' + record[Col.FTP.value] +
                               '"')
            rc = 0

        if rc == 0:
            if record[Col.VOLSER.value] == 'Pseudo':
                Log().logger.info(skip_message + 'VOLSER set to "Pseudo"')
                rc = 1
            elif record[Col.VOLSER.value] == 'Migrated':
                Log().logger.info(skip_message + 'VOLSER set to "Migrated"')
                rc = 1

        if rc == 0:
            if record[Col.DSORG.value] == 'PO' or record[
                    Col.DSORG.value] == 'PS':
                rc = 0
            elif record[Col.DSORG.value] == 'VSAM':
                if Context().prefix != '':
                    Log().logger.debug(
                        '[ftp] Prefix correctly specified for VSAM dataset download'
                    )
                    rc = 0
                else:
                    Log().logger.warning(
                        skip_message +
                        'PrefixError: -p or --prefix option must be specified for VSAM dataset download from mainframe'
                    )
                    rc = 1

            elif record[Col.DSORG.value] in unset_list:
                Log().logger.warning(skip_message + 'Missing DSORG parameter')
                rc = 1

            else:
                Log().logger.error(skip_message + 'Invalid DSORG parameter')
                rc = 1

        if rc == 0:
            Log().logger.debug('[ftp] Proceeding, dataset eligible: ' +
                               record[Col.DSN.value])

        return rc

    def _download_PS(self, dsn, rdwftp):
        """
            """
        ftp_command = rdwftp + '\nget ' + dsn
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _download_PO(self, dsn, rdwftp):
        """
            """
        # Creating the directory for the PO dataset
        if not os.path.exists(dsn):
            os.makedirs(dsn)
        os.chdir(dsn)
        ftp_command = rdwftp + '\ncd ' + dsn + '\nmget -c *'
        _, _, rc = Utils().execute_ftp_command(ftp_command)
        os.chdir(Context().datasets_directory)

        return rc

    def _download_VSAM(self, dsn, rdwftp):
        """
            """
        ftp_command = rdwftp + '\nget ' + Context().prefix + dsn + ' ' + dsn
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _download(self, record):
        """Main method for dataset download from mainframe to Linux server.

            Args:
                records: A 2D-list, the elements of the CSV file containing all the dataset data.

            Returns:
                A 2D-list, dataset data after all the changes applied in the download execution."""
        rc = 0
        # quote is an FTP option and RDW is dataset length for the given dataset
        # This conditional statement allow to retrieve record length for V (Variable) or VB (Variable Blocked) for successful download
        if record[Col.RECFM.value] != '' and record[Col.RECFM.value][0] == 'V':
            rdwftp = 'quote site rdw\n'
        else:
            rdwftp = ''

        start_time = time.time()

        Log().logger.info('[ftp] Downloading dataset: ' + record[Col.DSN.value])
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
        os.chdir(Context().datasets_directory)
        rc = 0

        # Skipping dataset download under specific conditions
        rc = self._analyze(record)
        if rc != 0:
            return rc

        # Downloading dataset from Mainframe using FTP
        rc = self._download(record)
        if rc == 0:
            self._storage_resource.write()

        Log().logger.debug('[ftp] Ending Job')

        return rc
