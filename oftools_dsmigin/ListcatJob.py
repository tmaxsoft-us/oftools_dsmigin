#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""This module runs the Listcat Job.

Typical usage example:
  job = ListcatJob(storage_resource)
  job.run()
"""

# Generic/Built-in modules
import time

# Third-party modules

# Owned modules
from .Context import Context
from .enums.ListcatEnum import LCol
from .enums.MessageEnum import Color, ErrorM, LogM
from .enums.MigrationEnum import MCol
from .GDG import GDG
from .handlers.ShellHandler import ShellHandler
from .Job import Job
from .Log import Log


class ListcatJob(Job):
    """A class used to run the Listcat Job.

    This class contains a run method that executes all the steps of the job. It handles both dataset info retrieval from the Mainframe as well as the VSAM dataset info retrieval from a listcat file.
    
    Attributes:
        Inherited from Job module.

    Methods:
        _analyze(record) -- Assesses listcat eligibility.
        _get_migrated(record, fields) -- Executes the FTP command on Mainframe to retrieve dataset info in the case where VOLSER is set to Migrated.
        _update_record(record, fields) -- Updates migration dataset record with parameters extracted from the FTP command output.
        _get_from_mainframe(record) -- Executes the FTP command on Mainframe to retrieve dataset info.
        _get_from_file(record) -- Reads the listcat CSV file to retrieve dataset info.
        run(record) -- Performs all the steps to exploit Mainframe info, the provided listcat file and updates the CSV file accordingly.
    """

    def _analyze(self, record):
        """Assesses listcat eligibility.

        This method double check multiple parameters in the migration dataset records to make sure that the given dataset listcat can be processed without error:
            - check IGNORE and LISTCAT status

        Arguments:
            record {list} -- Dataset migration record.

        Returns:
            integer -- Return code of the method.
        """
        Log().logger.debug(LogM.ELIGIBILITY.value %
                           (self._name, record[MCol.DSN.value]))
        skip_message = LogM.SKIP.value % ('listcat', record[MCol.DSN.value])

        if record[MCol.LISTCAT.value] == 'F':
            Log().logger.debug(LogM.COL_F.value % (self._name, 'LISTCAT'))
            rc = 0

        else:
            if record[MCol.IGNORE.value] == 'Y':
                Log().logger.info(skip_message + LogM.COL_Y.value % 'IGNORE')
                rc = 1
            elif record[MCol.LISTCAT.value] == 'N':
                Log().logger.debug(skip_message + LogM.COL_N.value % 'LISTCAT')
                rc = 1
            elif record[MCol.LISTCAT.value] in ('', 'Y'):
                Log().logger.debug(
                    LogM.COL_VALUE.value %
                    (self._name, 'LISTCAT', record[MCol.LISTCAT.value]))
                rc = 0
            else:
                rc = 0

        if rc == 0:
            Log().logger.debug(LogM.ELIGIBLE.value %
                               (self._name, record[MCol.DSN.value]))

        return rc

    def _get_migrated(self, record, fields):
        """Executes the FTP command on Mainframe to retrieve dataset info in the case where VOLSER is set to Migrated.

        Arguments:
            record {list} -- Dataset migration record.
            fields {list} -- Dataset parameters extracted from the FTP command.

        Returns:
            list -- The new list of parameters extracted from the FTP command after the recall.
        """
        fields = []

        Log().logger.info(LogM.MIGRATED.value % self._name)
        _, _, rc = ShellHandler().ftp_recall(fields[-1], self._name,
                                             Context().ip_address)

        if rc != 0:
            return fields

        Log().logger.debug(LogM.FTP_LS_AGAIN.value % self._name)
        stdout, _, rc = ShellHandler().ftp_ls(record[MCol.DSN.value],
                                              self._name,
                                              Context().ip_address)

        if rc == 0:
            lines = stdout.splitlines()
            if len(lines) > 1:
                fields = lines[1].split()
            else:
                Log().logger.debug(LogM.FTP_EMPTY.value % self._name)

        return fields

    def _update_record(self, record, fields):
        """Updates dataset migration record with parameters extracted from the FTP command.

        Arguments:
            record {list} -- Dataset migration record.
            fields {list} -- Dataset parameters extracted from the FTP command.
        """
        record[MCol.RECFM.value] = fields[-5]
        record[MCol.LRECL.value] = fields[-4]
        record[MCol.BLKSIZE.value] = fields[-3]
        record[MCol.DSORG.value] = fields[-2]
        record[MCol.VOLSER.value] = fields[0]

    def _get_from_mainframe(self, index, record):
        """Executes the FTP command on Mainframe to retrieve dataset info.

        It executes the ftp command and then the ls command on Mainframe to retrieve general info about dataset such as RECFM, LRECL, BLKSIZE, DSORG and VOLSER. It uses the sub method formatting_dataset_info to parse the output.

        Arguments:
            record {list} -- The given migration record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
        stdout, _, rc = ShellHandler().ftp_ls(record[MCol.DSN.value],
                                              self._name,
                                              Context().ip_address)

        try:
            if rc == 0:
                lines = stdout.splitlines()
                if len(lines) > 1:
                    fields = lines[1].split()

                    if len(fields) > 0:

                        if fields[0] == 'Migrated':
                            record[MCol.VOLSER.value] = fields[0]
                            fields = self._get_migrated(record, fields)

                        # New evaluation of len(fields) required after migrated update
                        if len(fields) == 0:
                            Log().logger.info(LogM.FIELDS_EMPTY.value %
                                              self._name)
                            status = 'FAILED'
                            color = Color.RED.value

                        elif len(fields) > 1:
                            status = 'SUCCESS'
                            color = Color.GREEN.value
                            # record[MCol.COPYBOOK.value] = record[MCol.DSN.value] + '.cpy'

                            if fields[1] == 'Tape':
                                Log().logger.info(LogM.TAPE.value % self._name)
                                record[MCol.VOLSER.value] = fields[1]

                            elif fields[0] == 'VSAM':
                                record[MCol.DSORG.value] = fields[0]

                            elif fields[0] == 'GDG':
                                Log().logger.info(LogM.GDG.value % self._name)
                                record[MCol.DSORG.value] = fields[0]
                                self._gdg = GDG(index, record)
                                self._gdg.get_dataset_records()

                            elif len(fields) > 7:
                                self._update_record(record, fields)

                            else:
                                raise SystemError(LogM.NOT_SUPPORTED.value %
                                                  self._name)
                        else:
                            raise SystemError(LogM.FIELDS_INCOMPLETE.value %
                                              self._name)
                    else:
                        raise SystemError(LogM.FIELDS_EMPTY.value % self._name)
                else:
                    raise SystemError(LogM.FTP_EMPTY.value % self._name)
            elif rc == -1:
                raise SystemError(ErrorM.LISTCAT_FTP.value %
                                  record[MCol.DSN.value])
            else:
                raise SystemError()

        except SystemError as e:
            if rc == 0:
                Log().logger.info(e)
                rc = -1
            elif rc == -1:
                Log().logger.error(e)

            status = 'FAILED'
            color = Color.RED.value

        Log().logger.info(color + LogM.LISTCAT_MAINFRAME.value % status)

        return rc

    def _get_from_file(self, record):
        """Reads the listcat CSV file to retrieve dataset info.

            First, this method search for the dataset in the listcat CSV file. If it finds the dataset, it updates the corresponding migration record. This method is used only for VSAM datasets.

            Arguments:
                record {list} -- The given migration record containing dataset info.

            Returns:
                integer -- Return code of the method.
            """
        dsn = record[MCol.DSN.value]

        #? Handle FileNotFound before doing that, because tried to access .keys() on a NoneType object is raising an exception
        if dsn in Context().listcat.data.keys():
            Log().logger.debug(LogM.DATASET_FOUND.value % self._name)

            listcat_record = [dsn] + Context().listcat.data[dsn]

            record[MCol.RECFM.value] = listcat_record[LCol.RECFM.value]
            record[MCol.VSAM.value] = listcat_record[LCol.VSAM.value]
            record[MCol.KEYOFF.value] = listcat_record[LCol.KEYOFF.value]
            record[MCol.KEYLEN.value] = listcat_record[LCol.KEYLEN.value]
            record[MCol.MAXLRECL.value] = listcat_record[LCol.MAXLRECL.value]
            record[MCol.AVGLRECL.value] = listcat_record[LCol.AVGLRECL.value]
            record[MCol.CISIZE.value] = listcat_record[LCol.CISIZE.value]
            record[MCol.CATALOG.value] = listcat_record[LCol.CATALOG.value]

            status = 'SUCCESS'
            color = Color.GREEN.value
            rc = 0
        else:
            Log().logger.info(LogM.DATASET_NOT_FOUND.value % self._name)
            status = 'FAILED'
            color = Color.RED.value
            rc = -1

        Log().logger.info(color + LogM.LISTCAT_FILE.value % status)

        return rc

    def run(self, record, index):
        """Performs all the steps to exploit Mainframe info, the provided listcat file and updates the migration records accordingly.

            It first run the analyze method to check if the given dataset is eligible for listcat. Then it executes the FTP command to get the dataset info from the Mainframe and retrieves data from a listcat file, this last step being for VSAM datasets only. Finally, it writes the changes to the CSV file.

            Arguments:
                record {list} -- Migration record containing dataset info.
                index {integer} -- Position of the record in the Context().records list.

            Returns:  
                integer -- Return code of the job.
            """
        Log().logger.debug(LogM.START_JOB.value % self._name)
        rc1, rc2 = 0, 0

        # Skipping dataset listcat under specific conditions
        rc = self._analyze(record)
        if rc != 0:
            return rc

        start_time = time.time()

        # Retrieve info from mainframe using FTP
        if Context().ip_address != None:
            rc1 = self._get_from_mainframe(index, record)

        # Retrieving info from listcat file for VSAM datasets
        if record[MCol.DSORG.value] == 'VSAM':
            rc2 = self._get_from_file(record)

        # Processing the result of the listcat
        if rc1 == 0 and rc2 == 0:
            record[MCol.LISTCATDATE.value] = Context().time_stamp
            if record[MCol.LISTCAT.value] != 'F':
                record[MCol.LISTCAT.value] = 'N'
            status = 'SUCCESS'
            color = Color.GREEN.value
            rc = 0
        #TODO Return codes study
        # elif rc1 != 0 and rc2 != 0:
        #     status = 'FAILED'
        else:
            status = 'FAILED'
            color = Color.RED.value
            if rc1 != 0:
                rc = rc1
            else:
                rc = rc2

        if record[MCol.DSORG.value] == 'GDG':
            self._gdg.update_listcat_result()

        elapsed_time = time.time() - start_time
        Log().logger.info(color + LogM.LISTCAT_STATUS.value %
                          (status, round(elapsed_time, 4)))

        Log().logger.debug(LogM.END_JOB.value % self._name)

        return rc