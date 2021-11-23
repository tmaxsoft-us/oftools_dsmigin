#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This modules runs the FTP Job.

    Typical usage example:
        job = FTPJob(storage_resource)
        job.run()
    """

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
    """A class used to run the FTP Job.

        This class contains a run method that executes all the steps of the job.

        Attributes:
            Inherited from Job module.

        Methods:
            _analyze(record) -- Assesses download eligibility.
            _download_PS(dsn, rdwftp) -- Downloads dataset with DSORG set to PS.
            _download_PO(dsn, rdwftp) -- Downloads dataset with DSORG set to PO.
            _download_VSAM(dsn, rdwftp) -- Downloads dataset with DSORG set to VSAM.
            _download_tape(record, rdwftp) -- Downloads dataset with VOLSER set to Tape.
            _download(record) -- Main method for dataset download from mainframe to Linux server.
            run(record) -- Performs all the steps to download datasets using FTP and updates the CSV file.
        """

    def _analyze(self, record):
        """Assesses download eligibility. 

            This method double check multiple parameters in the migration dataset records to make sure that the given dataset download can be processed without error:
                - check missing information
                - check IGNORE, LISTCATDATE and FTP columns status
                - check VOLSER column status, the dataset will be skipped if it is equal to Pseudo or Migrated
                - check DSORG column status, and the prefix if the given dataset is a VSAM dataset
                - check VOLSER column to see if the dataset is in Tape volume, and trigger the appropriate download method

            Arguments:
                record {list} -- The given migration record containing dataset info, which needs a verification prior download.
            
            Returns:
                integer - Return code of the method.
            """
        Log().logger.debug('[ftp] Assessing dataset eligibility: ' +
                           record[Col.DSN.value])
        rc = 0

        unset_list = ('', ' ')
        skip_message = '[ftp] Skipping dataset: ' + record[Col.DSN.value] + ': '

        if record[Col.FTP.value] == 'F':
            Log().logger.debug('[ftp] FTP set to "F"')
            rc = 0

        else:
            if record[Col.IGNORE.value] == 'Y':
                Log().logger.info(skip_message + 'IGNORE set to "Y"')
                rc = 1
            elif record[Col.LISTCATDATE.value] == '':
                Log().logger.info('[ftp] LISTCATDATE not set')
                rc = 0
            elif record[Col.FTP.value] == 'N':
                Log().logger.debug(skip_message + 'FTP set to "N"')
                rc = 1
            elif record[Col.FTP.value] in ('', 'Y'):
                Log().logger.debug('[ftp] FTP set to "' +
                                   record[Col.FTP.value] + '"')
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
                elif record[Col.DSORG.value] == 'GDG':
                    Log().logger.warning(
                        skip_message +
                        'DSORG set to "GDG": Ignoring GDG base for download')
                    record[Col.FTPDATE.value] = Context().timestamp
                    record[Col.FTPDURATION.value] = '0'
                    record[Col.FTP.value] = 'N'
                    rc = 1

                elif record[Col.DSORG.value] in unset_list:
                    if record[Col.VOLSER.value] == 'Tape':
                        Log().logger.debug(
                            '[ftp] VOLSER set to "Tape": Dowloading and retrieving dataset info'
                        )
                        rc = 0
                    else:
                        Log().logger.warning(skip_message +
                                             'Missing DSORG parameter')
                        rc = 1

                else:
                    Log().logger.error(skip_message + 'Invalid DSORG parameter')
                    rc = 1

        if rc == 0:
            Log().logger.debug('[ftp] Proceeding, dataset eligible: ' +
                               record[Col.DSN.value])

        return rc

    def _download_PS(self, dsn, rdwftp):
        """Downloads dataset with DSORG set to PS.

            Arguments:
                dsn {string} -- Dataset name.
                rdwftp {string} -- Additional ftp command for dataset with RECFM set to VB.

            Returns:
                integer -- Return code of the method.
            """
        ftp_command = rdwftp + '\nget ' + dsn
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _download_PO(self, dsn, rdwftp):
        """Downloads dataset with DSORG set to PO.

            Arguments:
                dsn {string} -- Dataset name.
                rdwftp {string} -- Additional ftp command for dataset with RECFM set to VB.

            Returns:
                integer -- Return code of the method.
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
        """Downloads dataset with DSORG set to VSAM.

            It is not dowloading directly the VSAM dataset but the flat file where the VSAM dataset has been unloaded.

            Arguments:
                dsn {string} -- Dataset name.
                rdwftp {string} -- Additional ftp command for dataset with RECFM set to VB.

            Returns:
                integer -- Return code of the method.
            """
        ftp_command = rdwftp + '\nget ' + Context().prefix + dsn + ' ' + dsn
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _download_tape(self, record, rdwftp):
        """Downloads dataset with VOLSER set to Tape.

            This method does not only download the given dataset but also retrieves information about it, only of the dataset has a fixed block length.

            Arguments:
                record {list} -- The given migration record containing dataset info.
                rdwftp {string} -- Additional ftp command for dataset with RECFM set to VB.

            Returns:
                integer -- Return code of the method.
            """
        dsn = record[Col.DSN.value]
        ftp_command = rdwftp + '\nget ' + dsn
        stdout, _, rc = Utils().execute_ftp_command(ftp_command)

        if rc == 0:
            ftp_result = stdout.splitlines()
            if len(ftp_result) > 2:
                fields = ftp_result[3].split()

                if len(fields) > 6:
                    if fields[5] == 'FIXrecfm':
                        Log().logger.info(
                            '[ftp] Downloaded dataset from Tape: RECFM set to FB'
                        )
                        record[Col.RECFM.value] = 'FB'
                        record[Col.LRECL.value] = fields[6]
                else:
                    Log().logger.warning(
                        '[ftp] Downloaded dataset from Tape: FIXrecfm string not found: RECFM set to VB'
                    )
                    Log().logger.warning(
                        '[ftp] VB dataset incorrectly downloaded. Please run FTP again for the given dataset'
                    )
                    record[Col.RECFM.value] = 'VB'
                    rc = -2

        return rc

    def _download(self, record):
        """Main method for dataset download from mainframe to Linux server.

            Arguments:
                record {list} -- The given migration record containing dataset info.

            Returns:
                integer -- Return code of the method.
            """
        rc = 0
        # quote is an FTP option and RDW is dataset length for the given dataset
        # This conditional statement allow to retrieve record length for V (Variable) or VB (Variable Blocked) for successful download
        if record[Col.RECFM.value] != '' and record[Col.RECFM.value][0] == 'V':
            if record[Col.VOLSER.value] == 'Tape':
                rdwftp = 'quote SITE RDW READTAPEFORMAT=V\n'
            else:
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
        elif record[Col.VOLSER.value] == 'Tape':
            rc = self._download_tape(record, rdwftp)

        elapsed_time = time.time() - start_time

        # Processing the result of the download
        if rc == 0:
            status = 'SUCCESS'
            record[Col.FTPDATE.value] = Context().timestamp
            record[Col.FTPDURATION.value] = str(round(elapsed_time, 4))
            if record[Col.FTP.value] != 'F':
                record[Col.FTP.value] = 'N'
        elif rc == -1:
            Log().logger.error(
                '[ftp] FTPDownloadError: Cannot proceed with dataset: ' +
                record[Col.DSN.value])
            status = 'FAILED'
        else:
            status = 'FAILED'

        Log().logger.info('DOWNLOAD ' + status + ' (' +
                          str(round(elapsed_time, 4)) + ' s)')

        return rc

    def run(self, _, record):
        """Performs all the steps to download datasets using FTP and updates the CSV file.

            It first run the analyze method to check if the given dataset is eligible for download. Then, it executes the FTP command to download it and updates the FTP status (success or fail) at the same time. Finally, it writes the changes to the CSV file.

            Arguments:
                record {list} -- The given migration record containing dataset info.

            Returns: 
                integer -- Return code of the job."""
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
