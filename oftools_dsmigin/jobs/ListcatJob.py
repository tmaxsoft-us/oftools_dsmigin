#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""This module runs the Listcat Job.

Typical usage example:
  job = ListcatJob(record)
  job.run()
"""

# Generic/Built-in modules
import time

# Third-party modules

# Owned modules
from ..Context import Context
from ..enums.CSV import LCol, MCol
from ..enums.Message import Color, ErrorM, LogM
from ..GDG import GDG
from ..handlers.ListcatHandler import ListcatHandler
from ..handlers.ShellHandler import ShellHandler
from .Job import Job
from ..Log import Log


class ListcatJob(Job):
    """A class used to run the Listcat Job.

    This class contains a run method that executes all the steps of the job. It
    handles both dataset info retrieval from the Mainframe as well as the VSAM
    dataset info retrieval from a listcat file.

    Attributes:
        Inherited from Job module.

    Methods:
        _analyze(record) -- Assesses listcat eligibility.
        _get_from_mainframe(record) -- Executes the FTP command on Mainframe to
            retrieve dataset info.
        _get_from_file(record) -- Reads the listcat CSV file to retrieve
            dataset info.
        run(record) -- Performs all the steps to exploit Mainframe info, the
            provided listcat file and updates the CSV file accordingly.
    """

    def _analyze(self, record):
        """Assesses listcat eligibility.

        This method double check multiple parameters in the migration dataset
        records to make sure that the given dataset listcat can be processed
        without error:
            - check IGNORE and LISTCAT status

        Arguments:
            record {list} -- Dataset migration record.

        Returns:
            integer -- Return code of the method.
        """
        Log().logger.debug(LogM.ELIGIBILITY.value %
                           (self._name, record[MCol.DSN.value]))
        skip_message = LogM.SKIP_DATASET.value % ('listcat', record[MCol.DSN.value])

        if record[MCol.LISTCAT.value] == 'F':
            Log().logger.debug(LogM.COL_F.value % (self._name, 'LISTCAT'))
            status = 0

        else:
            if record[MCol.IGNORE.value] == 'Y':
                Log().logger.info(skip_message + LogM.COL_Y.value % 'IGNORE')
                status = 1
            elif record[MCol.LISTCAT.value] == 'N':
                Log().logger.debug(skip_message + LogM.COL_N.value % 'LISTCAT')
                status = 1
            elif record[MCol.LISTCAT.value] in ('', 'Y'):
                Log().logger.debug(
                    LogM.COL_VALUE.value %
                    (self._name, 'LISTCAT', record[MCol.LISTCAT.value]))
                status = 0
            else:
                status = 0

        if status == 0:
            Log().logger.debug(LogM.ELIGIBLE.value %
                               (self._name, record[MCol.DSN.value]))

        return status

    def _process_vsam(self, record, fields):
        """
        """
        record[MCol.DSORG.value] = fields[0]

    def _process_gdg(self, index, record, fields):
        """
        """
        record[MCol.DSORG.value] = fields[0]
        self._gdg = GDG(index, record)
        self._gdg.get_from_mainframe()

    def _get_from_mainframe(self, index, record):
        """Executes the FTP command on Mainframe to retrieve dataset info.

        It executes the ftp command and then the ls command on Mainframe to
        retrieve general info about dataset such as RECFM, LRECL, BLKSIZE,
        DSORG and VOLSER. It uses the sub method formatting_dataset_info to
        parse the output.

        Arguments:
            record {list} -- The given migration record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
        stdout, _, status = ShellHandler().ftp_ls(record[MCol.DSN.value],
                                              self._name,
                                              Context().ip_address)

        try:
            if status == 0:
                lines = stdout.splitlines()
                if len(lines) > 1:
                    fields = lines[1].split()

                    if len(fields) > 0:
                        if fields[0] == 'Migrated':
                            fields = ListcatHandler().get_migrated(
                                record, self._name,
                                Context().ip_address)

                        # New evaluation of len(fields) required after migrated update
                        if len(fields) == 0:
                            Log().logger.info(LogM.FIELDS_EMPTY.value %
                                              self._name)
                            result = 'FAILED'
                            color = Color.RED.value

                        elif len(fields) > 1:
                            result = 'SUCCESS'
                            color = Color.GREEN.value

                            if fields[1] == 'Tape':
                                ListcatHandler().process_tape(
                                    record, fields, self._name)

                            elif fields[0] == 'VSAM':
                                self._process_vsam(record, fields)

                            elif fields[0] == 'GDG':
                                self._process_gdg(index, record, fields)

                            elif len(fields) > 7:
                                ListcatHandler().update_record(record, fields)

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
            elif status == -1:
                raise SystemError(ErrorM.LISTCAT_FTP.value %
                                  record[MCol.DSN.value])
            else:
                raise SystemError()

        except SystemError as err:
            if status == 0:
                Log().logger.info(err)
                status = -1
            else:
                Log().logger.error(err)

            result = 'FAILED'
            color = Color.RED.value

        Log().logger.info(color + LogM.LISTCAT_MAINFRAME_STATUS.value % result)

        return status

    def _get_from_file(self, record):
        """Reads the listcat CSV file to retrieve dataset info.

        First, this method search for the dataset in the listcat CSV file. If
        it finds the dataset, it updates the corresponding migration record.
        This method is used only for VSAM datasets.

        Arguments:
            record {list} -- Migration dataset record.

        Returns:
            integer -- Return code of the method.
        """
        dsn = record[MCol.DSN.value]

        if Context().listcat_records != {} and dsn in Context(
        ).listcat_records.keys():
            Log().logger.debug(LogM.DATASET_FOUND.value % self._name)

            listcat_record = Context().listcat_records[dsn]

            record[MCol.RECFM.value] = listcat_record[LCol.RECFM.value]
            record[MCol.VSAM.value] = listcat_record[LCol.VSAM.value]
            record[MCol.KEYOFF.value] = listcat_record[LCol.KEYOFF.value]
            record[MCol.KEYLEN.value] = listcat_record[LCol.KEYLEN.value]
            record[MCol.MAXLRECL.value] = listcat_record[LCol.MAXLRECL.value]
            record[MCol.AVGLRECL.value] = listcat_record[LCol.AVGLRECL.value]
            record[MCol.CISIZE.value] = listcat_record[LCol.CISIZE.value]
            record[MCol.CATALOG.value] = listcat_record[LCol.CATALOG.value]

            result = 'SUCCESS'
            color = Color.GREEN.value
            status = 0
        else:
            Log().logger.info(LogM.DATASET_NOT_FOUND.value % self._name)
            result = 'FAILED'
            color = Color.RED.value
            status = 0

        Log().logger.info(color + LogM.LISTCAT_FILE_STATUS.value % result)

        return status

    def _update_index_and_data(self, record):
        """Take the listcat extracted data to update the CSV records.

        It first updates the CSV records with different data regarding the VSAM
        datasets, data required for a successful migration of this type of
        dataset. Then, it also look for each VSAM datasets if there are the
        equivalent 'INDEX and 'DATA'. These datasets are not useful for
        migration, so the tool removes them.

        Arguments:
            record {list} -- The given listcat record containing dataset info.
        """
        index_and_data = [
            record[MCol.DSN.value] + '.INDEX', record[MCol.DSN.value] + '.DATA'
        ]

        for dsn in index_and_data:
            if dsn in Context().dsn_list:
                # Replace the value in the column named DSORG by VSAM in the records list
                record[MCol.DSORG.value] = 'VSAM'
                # Identify the position of the index DSN in the dsn_list
                i = Context().dsn_list.index(dsn)
                # Remove the line where this DSN appears in the records list
                Context().records.remove(Context().records[i])
                Log().logger.info(LogM.REMOVE_DATASET.value % (self._name, dsn))

    def run(self, record, index):
        """Performs all the steps to exploit Mainframe info, the provided listcat file and updates the migration records accordingly.

        It first run the analyze method to check if the given dataset is
        eligible for listcat. Then it executes the FTP command to get the
        dataset info from the Mainframe and retrieves data from a listcat file,
        this last step being for VSAM datasets only. Finally, it writes the
        changes to the CSV file.

        Arguments:
            record {list} -- Migration record containing dataset info.
            index {integer} -- Position of the record in the Context().records
                list.

        Returns:
            integer -- Return code of the job.
        """
        Log().logger.debug(LogM.START_JOB.value % self._name)
        status1, status2 = 0, 0

        # Skipping dataset listcat under specific conditions
        status = self._analyze(record)
        if status != 0:
            return status

        start_time = time.time()

        # Retrieve info from mainframe using FTP
        if Context().ip_address is not None:
            status1 = self._get_from_mainframe(index, record)

        # Retrieving info from listcat file for VSAM datasets
        if record[MCol.DSORG.value] == 'VSAM':
            if Context().listcat_records != {}:
                status2 = self._get_from_file(record)

            self._update_index_and_data(record)

        # Processing the result of the listcat
        if status1 == 0 and status2 == 0:
            record[MCol.LISTCATDATE.value] = Context().time_stamp
            if record[MCol.LISTCAT.value] != 'F':
                record[MCol.LISTCAT.value] = 'N'
            result = 'SUCCESS'
            color = Color.GREEN.value
            status = 0
        #TODO Return codes study
        # elif status1 != 0 and status2 != 0:
        #     result = 'FAILED'
        else:
            result = 'FAILED'
            color = Color.RED.value
            if status1 != 0:
                status = status1
            else:
                status = status2

        if record[MCol.DSORG.value] == 'GDG':
            self._gdg.update_listcat_result()

        elapsed_time = time.time() - start_time
        Log().logger.info(color + LogM.LISTCAT_STATUS.value %
                          (result, round(elapsed_time, 4)))

        Log().logger.debug(LogM.END_JOB.value % self._name)

        return status
