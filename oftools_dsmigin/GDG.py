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
from .enums.CSV import MCol
from .enums.Message import Color, ErrorM, LogM
from .handlers.ListcatHandler import ListcatHandler
from .handlers.ShellHandler import ShellHandler
from .Log import Log
from .Record import Record


class GDG(object):
    """A class used to run the Migration Job.

    This class contains a run method that executes all the steps of the job. It
    handles all tasks related to dataset migration which mainly depends on the
    dataset organization, the DSORG column of the CSV file.

    Attributes:
        _index {integer} -- The position of the record in the Context().records
            list.
        _record {list} -- The given migration record containing dataset info.
        _base {string} -- The GDG base name.
        _generations {2D-list} -- The FTP command output, one element of the
            list being one line, one line corresponding to one dataset info.
        _generations_count {integer} -- The number of generations successfully
            processed.

    Methods:
        __init__(record) -- Initializes all attributes of the class.
        _update_record(fields, record) -- Updates migration dataset record with
            parameters extracted from the FTP command output.
        get_dataset_records() -- Performs all the steps to exploit Mainframe
            info for GDG datasets only, and updates the migration records
            accordingly.
    """

    def __init__(self, index, record):
        """Initializes all attributes of the class.
        """
        self._name = "gdg"

        self._index = index
        self._record = record

        self._base = record[MCol.DSN.value]

        self._generations = []
        self._generations_count = 0

    def get_from_mainframe(self):
        """Performs all the steps to exploit Mainframe info for GDG datasets
        only, and updates the migration records accordingly.

        Returns:
            integer -- Return code of the method.
        """
        Log().logger.debug(LogM.GEN_FOR_BASE.value % self._base)
        ftp_cd_ls = "cd " + self._record[MCol.DSN.value] + "\nls"

        Log().logger.debug(LogM.COMMAND.value % (self._name, ftp_cd_ls))
        stdout, _, status = ShellHandler().execute_ftp_command(
            ftp_cd_ls,
            Context().ip_address)

        failed = False

        try:
            if status == 0:
                self._generations = stdout.splitlines()
                if len(self._generations) > 0:
                    for i in range(len(self._generations) - 1, -1, -1):
                        fields = self._generations[i].split()

                        if len(fields) > 0:
                            if bool(re.match(r"G[0-9]{4}V[0-9]{2}",
                                             fields[-1])):

                                generation = ["" for _ in range(len(MCol))]
                                generation[
                                    MCol.DSN.
                                    value] = self._base + "." + fields[-1]
                                generation[MCol.COPYBOOK.value] = self._record[
                                    MCol.COPYBOOK.value]
                                Log().logger.info(LogM.GEN_PROCESS.value %
                                                  generation[MCol.DSN.value])

                                if fields[0] == "Migrated":
                                    fields = ListcatHandler().get_migrated(
                                        generation, self._name,
                                        Context().ip_address, i)

                                # New evaluation of len(fields) required after
                                # migrated update
                                if len(fields) == 0:
                                    Log().logger.error(LogM.FIELDS_EMPTY.value %
                                                       self._name)
                                    result = "FAILED"
                                    color = Color.RED.value

                                elif len(fields) > 1:
                                    result = "SUCCESS"
                                    color = Color.GREEN.value

                                    if fields[1] == "Tape":
                                        ListcatHandler().process_tape(
                                            generation, fields, self._name)
                                    elif len(fields) > 7:
                                        ListcatHandler().update_record(
                                            generation, fields)
                                    else:
                                        Log().logger.error(
                                            LogM.NOT_SUPPORTED.value %
                                            self._name)
                                        result = "FAILED"
                                        color = Color.RED.value

                                else:
                                    Log().logger.error(
                                        LogM.FIELDS_INCOMPLETE.value %
                                        self._name)
                                    result = "FAILED"
                                    color = Color.RED.value
                                    failed = True

                                if result == "SUCCESS":
                                    Log().logger.debug(
                                        LogM.NEW_RECORD.value %
                                        generation[MCol.DSN.value])

                                    record = Record(MCol)
                                    record.columns = generation

                                    self._generations_count += 1
                                    Context().records.insert(
                                        self._index + self._generations_count,
                                        record)

                                Log().logger.info(color +
                                                  LogM.LISTCAT_GDG_GEN.value %
                                                  result)

                            elif fields[
                                    -1] == "Dsname" and self._generations_count > 0:
                                Log().logger.info(LogM.OLDEST_GEN.value)
                                result = "SUCCESS"
                                color = Color.GREEN.value
                                status = 0
                                break
                            elif fields[
                                    -1] == "Dsname" and self._generations_count == 0 and failed is False:
                                Log().logger.info(LogM.NO_GEN.value %
                                                  self._base)
                                result = "SUCCESS"
                                color = Color.GREEN.value
                                status = 0
                                break
                            elif fields[
                                    -1] == "Dsname" and self._generations_count == 0 and failed is True:
                                Log().logger.error(LogM.GEN_FAIL.value)
                                result = "FAILED"
                                color = Color.RED.value
                                status = -1
                                break
                            else:
                                Log().logger.debug(
                                    LogM.PATTERN_NOT_SUPPORTED.value %
                                    fields[-1])
                                Log().logger.debug(LogM.GEN_SKIP.value)
                                continue
                        else:
                            Log().logger.error(LogM.FIELDS_EMPTY.value %
                                               self._name)
                            continue

                        if self._generations_count >= Context().generations:
                            Log().logger.info(LogM.GEN_MAX.value)
                            result = "SUCCESS"
                            color = Color.GREEN.value
                            status = 0
                            break
                else:
                    raise SystemError(LogM.FTP_EMPTY.value % self._name)
            elif status == -1:
                raise SystemError(ErrorM.LISTCAT_FTP.value % self._base)
            else:
                raise SystemError()

        except SystemError as err:
            if status == 0:
                Log().logger.info(err)
                status = -1
            elif status == -1:
                Log().logger.error(err)

            result = "FAILED"
            color = Color.RED.value

        Log().logger.info(color + LogM.LISTCAT_GDG_STATUS.value % result)

        return status

    def update_listcat_result(self):
        """
        """
        start = self._index + 1
        end = start + self._generations_count

        for i in range(start, end, 1):
            generation_record = Context().records[i].columns
            generation_record[MCol.LISTCAT.value] = self._record[
                MCol.LISTCAT.value]
            generation_record[MCol.LISTCATDATE.value] = self._record[
                MCol.LISTCATDATE.value]
