#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Module .
    
Typical usage example:
"""

# Generic/Built-in modules
import re

# Third-party modules

# Owned modules
from .Context import Context
from .DatasetRecord import DatasetRecord
from .enums.MessageEnum import Color, ErrorM, LogM
from .enums.MigrationEnum import Col
from .handlers.ShellHandler import ShellHandler
from .ListcatJob import ListcatJob
from .Log import Log


class GDG(ListcatJob):
    """A class used to run the Migration Job.

    This class contains a run method that executes all the steps of the job. It handles all tasks related to dataset migration which mainly depends on the dataset organization, the DSORG column of the CSV file.

    Attributes:
        _index {integer} -- The position of the record in the Context().records list.
        _record {list} -- The given migration record containing dataset info.
        _base {string} -- The GDG base name.
        _generations {2D-list} -- The FTP command output, one element of the list being one line, one line corresponding to one dataset info.
        _generations_count {integer} -- The number of generations successfully processed.
        
    Methods:
        __init__(record) -- Initializes all attributes of the class.
        _get_migrated(record, fields, line_number) -- Executes the FTP command on Mainframe to retrieve dataset info in the case where VOLSER is set to Migrated.
        _update_record(fields, record) -- Updates migration dataset record with parameters extracted from the FTP command output.
        get_dataset_records() -- Performs all the steps to exploit Mainframe info for GDG datasets only, and updates the migration records accordingly.
    """

    def __init__(self, index, record):
        """Initializes all attributes of the class.
        """
        self._name = 'gdg'

        self._index = index
        self._record = record

        self._base = record[Col.DSN.value]

        self._generations = []
        self._generations_count = 0

    def _get_migrated(self, record, fields, line_number):
        """Executes the FTP command on Mainframe to retrieve dataset info in the case where VOLSER is set to Migrated.

        Arguments:
            record {list} -- Migration record containing dataset info.
            fields {list} -- List of parameters extracted from the FTP command.
            line_number {integer} -- The generation number, with a certain shift to match the appropriate line in the FTP command output.

        Returns:
            list -- The new list of parameters extracted from the FTP command after the recall.
        """
        Log().logger.info(LogM.MIGRATED.value % self._name)
        record[Col.VOLSER.value] = fields[0]
        ShellHandler().recall(self._base + '.' + fields[-1], self._name,
                              Context().ip_address)

        Log().logger.debug(LogM.FTP_LS_AGAIN.value % self._name)
        ftp_command = 'cd ' + self._base + '\nls'

        Log().logger.debug(LogM.COMMAND.value % (self._name, ftp_command))
        stdout, _, rc = ShellHandler().execute_ftp_command(
            ftp_command,
            Context().ip_address)

        if rc == 0:
            self._generations = stdout.splitlines()
            if len(self._generations) > 1:
                fields = self._generations[line_number].split()
            else:
                Log().logger.debug(LogM.FTP_EMPTY.value % self._name)
                fields = []
        else:
            fields = []

        return fields

    def get_dataset_records(self):
        """Performs all the steps to exploit Mainframe info for GDG datasets only, and updates the migration records accordingly.

        Returns:
            integer -- Return code of the method.
        """
        Log().logger.debug(LogM.GEN_FOR_BASE.value % self._base)
        ftp_command = 'cd ' + self._record[Col.DSN.value] + '\nls'
        Log().logger.debug('[gdg] ' + ftp_command)
        stdout, _, rc = ShellHandler().execute_ftp_command(
            ftp_command,
            Context().ip_address)

        failed = False

        try:
            if rc == 0:
                self._generations = stdout.splitlines()
                if len(self._generations) > 0:
                    for i in range(len(self._generations) - 1, -1, -1):
                        fields = self._generations[i].split()

                        if len(fields) > 0:
                            if bool(re.match(r"G[0-9]{4}V[0-9]{2}",
                                             fields[-1])):

                                generation_record = [
                                    '' for _ in range(len(Col))
                                ]
                                generation_record[
                                    Col.DSN.
                                    value] = self._base + '.' + fields[-1]
                                Log().logger.info(
                                    LogM.GEN_PROCESS.value %
                                    generation_record[Col.DSN.value])

                                if fields[0] == 'Migrated':
                                    fields = self._get_migrated(
                                        self._record, fields, i)

                                # New evaluation of len(fields) required after migrated update
                                if len(fields) == 0:
                                    Log().logger.info(LogM.FIELDS_EMPTY.value %
                                                      self._name)
                                    status = 'FAILED'
                                    color = Color.RED.value

                                elif len(fields) > 1:
                                    status = 'SUCCESS'
                                    color = Color.GREEN.value

                                    if fields[1] == 'Tape':
                                        Log().logger.info(LogM.TAPE.value %
                                                          self._name)
                                        generation_record[
                                            Col.VOLSER.value] = fields[1]
                                    elif len(fields) > 7:
                                        self._update_record(
                                            generation_record, fields)
                                    else:
                                        Log().logger.info(
                                            LogM.NOT_SUPPORTED.value %
                                            self._name)
                                        status = 'FAILED'
                                        color = Color.RED.value

                                else:
                                    Log().logger.info(
                                        LogM.FIELDS_INCOMPLETE.value %
                                        self._name)
                                    status = 'FAILED'
                                    color = Color.RED.value
                                    failed = True

                                if status == 'SUCCESS':
                                    Log().logger.debug(
                                        LogM.NEW_RECORD.value %
                                        generation_record[Col.DSN.value])

                                    new_record = DatasetRecord(Col)
                                    new_record.columns = generation_record

                                    self._generations_count += 1
                                    Context().records.insert(
                                        self._index + self._generations_count,
                                        new_record)

                                Log().logger.info(color +
                                                  LogM.LISTCAT_GDG_GEN.value %
                                                  status)

                            elif fields[
                                    -1] == 'Dsname' and self._generations_count > 0:
                                Log().logger.info(LogM.OLDEST_GEN.value)
                                status = 'SUCCESS'
                                color = Color.GREEN.value
                                rc = 0
                                break
                            elif fields[
                                    -1] == 'Dsname' and self._generations_count == 0 and failed is False:
                                Log().logger.info(LogM.NO_GEN.value %
                                                  self._base)
                                status = 'SUCCESS'
                                color = Color.GREEN.value
                                rc = 0
                                break
                            elif fields[
                                    -1] == 'Dsname' and self._generations_count == 0 and failed is True:
                                Log().logger.info(LogM.GEN_FAIL.value)
                                status = 'FAILED'
                                color = Color.RED.value
                                rc = -1
                                break
                            else:
                                Log().logger.debug(
                                    LogM.PATTERN_NOT_SUPPORTED.value %
                                    fields[-1])
                                Log().logger.debug(LogM.GEN_SKIP.value)
                                continue
                        else:
                            Log().logger.info(LogM.FIELDS_EMPTY.value %
                                              self._name)
                            continue

                        if self._generations_count >= Context().generations:
                            Log().logger.info(LogM.GEN_MAX.value)
                            status = 'SUCCESS'
                            color = Color.GREEN.value
                            rc = 0
                            break
                else:
                    raise SystemError(LogM.FTP_EMPTY.value % self._name)
            elif rc == -1:
                raise SystemError(ErrorM.LISTCAT_FTP.value % self._base)
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

        Log().logger.info(color + LogM.LISTCAT_GDG_STATUS.value % status)

        return rc

    def update_listcat_result(self):
        """
        """
        for i in range(self._index + 1,
                       self._index + 1 + self._generations_count, 1):
            generation_record = Context().records[i].columns
            generation_record[Col.COPYBOOK.value] = self._record[
                Col.COPYBOOK.value]
            generation_record[Col.LISTCAT.value] = self._record[
                Col.LISTCAT.value]
            generation_record[Col.LISTCATDATE.value] = self._record[
                Col.LISTCATDATE.value]
