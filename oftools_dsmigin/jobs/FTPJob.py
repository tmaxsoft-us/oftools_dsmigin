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
from ..Context import Context
from ..enums.CSV import MCol
from ..enums.Message import Color, ErrorM, LogM
from ..handlers.FileHandler import FileHandler
from ..handlers.ShellHandler import ShellHandler
from .Job import Job
from ..Log import Log


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
        _download_tape(record, rdwftp) -- Downloads dataset with VOLSER set to
            Tape.
        _download(record) -- Main method for dataset download from mainframe to
            Linux server.
        run(record) -- Performs all the steps to download datasets using FTP
            and updates the CSV file.
    """

    def _analyze(self, record):
        """Assesses download eligibility.

        This method double check multiple parameters in the migration dataset
        records to make sure that the given dataset download can be processed
        without error:
            - check missing information
            - check IGNORE, LISTCATDATE and FTP columns status
            - check VOLSER column status, the dataset will be skipped if it is
                equal to Pseudo or Migrated
            - check DSORG column status, and the prefix if the given dataset is
                a VSAM dataset
            - check VOLSER column to see if the dataset is in Tape volume, and
                trigger the appropriate download method

        Arguments:
            record {list} -- The given migration record containing dataset
                info, which needs a verification prior download.

        Returns:
            integer - Return code of the method.
        """
        Log().logger.debug(LogM.ELIGIBILITY.value %
                           (self._name, record[MCol.DSN.value]))
        status = 0

        unset_list = ('', ' ')
        skip_message = LogM.SKIP_DATASET.value % (self._name,
                                                  record[MCol.DSN.value])

        if record[MCol.FTP.value] == 'F':
            Log().logger.debug(LogM.COL_F.value % (self._name, 'FTP'))
            status = 0

        else:
            if record[MCol.IGNORE.value] == 'Y':
                Log().logger.info(skip_message + LogM.COL_Y.value % 'IGNORE')
                status = 1
            elif record[MCol.LISTCATDATE.value] == '':
                Log().logger.info('[ftp] ' +
                                  LogM.COL_NOT_SET.value % 'LISTCATDATE')
                status = 0
            elif record[MCol.FTP.value] == 'N':
                Log().logger.debug(skip_message + LogM.COL_N.value % 'FTP')
                status = 1
            elif record[MCol.FTP.value] in ('', 'Y'):
                Log().logger.debug(LogM.COL_VALUE.value %
                                   (self._name, 'FTP', record[MCol.FTP.value]))
                status = 0

            if status == 0:
                if record[MCol.VOLSER.value] == 'Pseudo':
                    Log().logger.info(skip_message +
                                      LogM.VOLSER.value % 'Pseudo')
                    status = 1
                elif record[MCol.VOLSER.value] == 'Migrated':
                    Log().logger.info(skip_message +
                                      LogM.VOLSER.value % 'Migrated')
                    status = 1

            if status == 0:
                if record[MCol.DSORG.value] == 'PO' or record[
                        MCol.DSORG.value] == 'PS':
                    status = 0
                elif record[MCol.DSORG.value] == 'VSAM':
                    if Context().prefix != '':
                        Log().logger.debug(LogM.PREFIX_OK.value % self._name)
                        status = 0
                    else:
                        Log().logger.warning(skip_message +
                                             LogM.PREFIX_MISSING.value)
                        status = 1
                elif record[MCol.DSORG.value] == 'GDG':
                    Log().logger.info(skip_message +
                                      LogM.DSORG_GDG.value % self._name)
                    record[MCol.FTPDATE.value] = Context().time_stamp
                    record[MCol.FTPDURATION.value] = '0'
                    record[MCol.FTP.value] = 'N'
                    status = 1

                elif record[MCol.DSORG.value] in unset_list:
                    if record[MCol.VOLSER.value] == 'Tape':
                        Log().logger.debug(LogM.VOLSER_TAPE.value % self._name)
                        status = 0
                    else:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'DSORG')
                        status = 1

                else:
                    Log().logger.error(skip_message + LogM.COL_INVALID.value %
                                       record[MCol.DSORG.value])
                    status = 1

        if status == 0:
            Log().logger.debug(LogM.ELIGIBLE.value %
                               (self._name, record[MCol.DSN.value]))

        return status

    def _download_ps(self, dsn, rdwftp):
        """Downloads dataset with DSORG set to PS.

        Arguments:
            dsn {string} -- Dataset name.
            rdwftp {string} -- Additional ftp command for dataset with RECFM
                set to VB.

        Returns:
            integer -- Return code of the method.
        """
        ftp_command = rdwftp + '\nget ' + dsn

        Log().logger.debug(LogM.COMMAND.value % (self._name, ftp_command))
        _, _, status = ShellHandler().execute_ftp_command(
            ftp_command,
            Context().ip_address)

        return status

    def _download_po(self, dsn, rdwftp):
        """Downloads dataset with DSORG set to PO.

        Arguments:
            dsn {string} -- Dataset name.
            rdwftp {string} -- Additional ftp command for dataset with RECFM
                set to VB.

        Returns:
            integer -- Return code of the method.
        """
        FileHandler().create_directory(dsn, 'po')
        os.chdir(dsn)

        ftp_command = rdwftp + '\ncd ' + dsn + '\nmget -c *'

        Log().logger.debug(LogM.COMMAND.value % (self._name, ftp_command))
        _, _, status = ShellHandler().execute_ftp_command(
            ftp_command,
            Context().ip_address)
        os.chdir(Context().datasets_directory)

        return status

    def _download_vsam(self, dsn, rdwftp):
        """Downloads dataset with DSORG set to VSAM.

        It is not downloading directly the VSAM dataset but the flat file where
        the VSAM dataset has been unloaded.

        Arguments:
            dsn {string} -- Dataset name.
            rdwftp {string} -- Additional ftp command for dataset with RECFM
                set to VB.

        Returns:
            integer -- Return code of the method.
        """
        ftp_command = rdwftp + '\nget ' + Context().prefix + dsn + ' ' + dsn

        Log().logger.debug(LogM.COMMAND.value % (self._name, ftp_command))
        _, _, status = ShellHandler().execute_ftp_command(
            ftp_command,
            Context().ip_address)

        return status

    def _download_tape(self, record, rdwftp):
        """Downloads dataset with VOLSER set to Tape.

        This method does not only download the given dataset but also retrieves
            information about it, only of the dataset has a fixed block length.

        Arguments:
            record {list} -- Migration record containing dataset info.
            rdwftp {string} -- Additional ftp command for dataset with RECFM
                set to VB.

        Returns:
            integer -- Return code of the method.
        """
        dsn = record[MCol.DSN.value]
        ftp_command = rdwftp + '\nget ' + dsn

        Log().logger.debug(LogM.COMMAND.value % (self._name, ftp_command))
        stdout, _, status = ShellHandler().execute_ftp_command(
            ftp_command,
            Context().ip_address)

        if status == 0:
            ftp_result = stdout.splitlines()
            if len(ftp_result) > 2:
                fields = ftp_result[3].split()

                if len(fields) > 6:
                    if fields[5] == 'FIXrecfm':
                        Log().logger.info(LogM.TAPE_FB.value % self._name)
                        record[MCol.RECFM.value] = 'FB'
                        record[MCol.LRECL.value] = fields[6]
                else:
                    Log().logger.error(LogM.TAPE_VB.value % self._name)
                    Log().logger.error(LogM.TAPE_INCORRECT.value %
                                       (self._name, record[MCol.DSN.value]))
                    record[MCol.RECFM.value] = 'VB'
                    status = -2

        return status

    def _download(self, record):
        """Main method for dataset download from mainframe to Linux server.

        Arguments:
            record {list} -- Migration record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
        status = 0
        # quote is an FTP option and RDW is dataset length for the given dataset
        # This conditional statement allow to retrieve record length for V
        # (Variable) or VB (Variable Blocked) for successful download
        if record[MCol.RECFM.value] != '' and record[
                MCol.RECFM.value][0] == 'V':
            if record[MCol.VOLSER.value] == 'Tape':
                rdwftp = 'quote SITE RDW READTAPEFORMAT=V\n'
            else:
                rdwftp = 'quote site rdw\n'
        else:
            rdwftp = ''

        start_time = time.time()

        Log().logger.info(LogM.DOWNLOAD.value %
                          (self._name, record[MCol.DSN.value]))
        if record[MCol.DSORG.value] == 'PS':
            status = self._download_ps(record[MCol.DSN.value], rdwftp)
        elif record[MCol.DSORG.value] == 'PO':
            status = self._download_po(record[MCol.DSN.value], rdwftp)
        elif record[MCol.DSORG.value] == 'VSAM':
            status = self._download_vsam(record[MCol.DSN.value], rdwftp)
        elif record[MCol.VOLSER.value] == 'Tape':
            status = self._download_tape(record, rdwftp)

        elapsed_time = time.time() - start_time

        # Processing the result of the download
        if status == 0:
            record[MCol.FTPDATE.value] = Context().time_stamp
            record[MCol.FTPDURATION.value] = str(round(elapsed_time, 4))
            if record[MCol.FTP.value] != 'F':
                record[MCol.FTP.value] = 'N'

            result = 'SUCCESS'
            color = Color.GREEN.value
        elif status == -1:
            Log().logger.error(ErrorM.FTP_DOWNLOAD.value %
                               record[MCol.DSN.value])
            result = 'FAILED'
            color = Color.RED.value
        else:
            result = 'FAILED'
            color = Color.RED.value

        Log().logger.info(color + LogM.FTP_STATUS.value %
                          (result, round(elapsed_time, 4)))

        return status

    def run(self, record, _):
        """Performs all the steps to download datasets using FTP and updates
            the CSV file.

        It first run the analyze method to check if the given dataset is
        eligible for download. Then, it executes the FTP command to download it
        and updates the FTP status (success or fail) at the same time. Finally,
        it writes the changes to the CSV file.

        Arguments:
            record {list} -- Migration record containing dataset info.

        Returns:
            integer -- Return code of the job.
        """
        Log().logger.debug(LogM.START_JOB.value % self._name)
        os.chdir(Context().datasets_directory)

        # Skipping dataset download under specific conditions
        status = self._analyze(record)
        if status != 0:
            return status

        # Downloading dataset from Mainframe using FTP
        status = self._download(record)

        Log().logger.debug(LogM.END_JOB.value % self._name)

        return status
