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
from .Log import Log
from .MigrationEnum import Col
from .Utils import Utils


class GDG(object):
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
            _recall(dataset_name) -- Executes FTP command to make dataset available to download.
            _get_migrated(record, fields, line_number) -- Executes the FTP command on Mainframe to retrieve dataset info in the case where VOLSER is set to Migrated.
            _update_record(fields, record) -- Updates migration dataset record with parameters extracted from the FTP command output.
            get_dataset_records() -- Performs all the steps to exploit Mainframe info for GDG datasets only, and updates the migration records accordingly.
    """

    def __init__(self, index, record):
        """Initializes all attributes of the class.
        """
        self._index = index
        self._record = record

        self._base = record[Col.DSN.value]

        self._generations = []
        self._generations_count = 0

    def _recall(self, dataset_name):
        """Executes FTP command to make dataset available to download.

            If a dataset has VOLSER set to 'Migrated', the program executes this recall method just to open the diretory containing the dataset to trigger download execution from the mainframe.

            Arguments:
                dataset_name {string} -- Dataset name.

            Returns:
                integer -- Return code of the method.
            """
        Log().logger.info('[listcat] Recalling migrated dataset: ' +
                          dataset_name)
        ftp_command = 'cd ' + dataset_name
        Log().logger.debug('[listcat] ' + ftp_command)
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _get_migrated(self, record, fields, line_number):
        """Executes the FTP command on Mainframe to retrieve dataset info in the case where VOLSER is set to Migrated.

            Arguments:
                record {list} -- The given migration record containing dataset info.
                fields {list} -- The list of parameters extracted from the FTP command currently being processed.
                line_number {integer} -- The generation number, with a certain shift to match the appropriate line in the FTP command output.

            Returns:
                list -- The new list of parameters extracted from the FTP command after the recall.
            """
        Log().logger.info('[gdg] Dataset marked as "Migrated"')
        record[Col.VOLSER.value] = fields[0]
        self._recall(fields[-1])

        Log().logger.debug('[gdg] Running the ftp ls command once again')
        ftp_command = 'cd ' + self._base + '\nls'
        Log().logger.debug('[gdg] ' + ftp_command)
        stdout, _, rc = Utils().execute_ftp_command(ftp_command)

        if rc == 0:
            self._generations = stdout.splitlines()
            if len(self._generations) > 1:
                fields = self._generations[line_number].split()
            else:
                Log().logger.debug('[gdg] FTP result empty')
                fields = []
        else:
            fields = []

        return fields

    def _update_record(self, record, fields):
        """Updates migration dataset record with parameters extracted from the FTP command output.

        Arguments:
            record {list} -- The given migration record containing dataset info.
            fields {list} -- The list of parameters extracted from the FTP command currently being processed.
        """
        record[Col.RECFM.value] = fields[-5]
        record[Col.LRECL.value] = fields[-4]
        record[Col.BLKSIZE.value] = fields[-3]
        record[Col.DSORG.value] = fields[-2]
        record[Col.VOLSER.value] = fields[0]

    def get_dataset_records(self):
        """Performs all the steps to exploit Mainframe info for GDG datasets only, and updates the migration records accordingly.

            Returns:
                integer -- Return code of the method.
            """
        Log().logger.debug('[gdg] Getting generations for the dataset: ' +
                           self._base)
        ftp_command = 'cd ' + self._record[Col.DSN.value] + '\nls'
        Log().logger.debug('[gdg] ' + ftp_command)
        stdout, _, rc = Utils().execute_ftp_command(ftp_command)

        failed = False

        if rc == 0:
            self._generations = stdout.splitlines()
            if len(self._generations) > 0:
                for i in range(len(self._generations) - 1, -1, -1):
                    fields = self._generations[i].split()

                    if len(fields) > 0:
                        if bool(re.match(r"G[0-9]{4}V[0-9]{2}", fields[-1])):

                            generation_record = ['' for _ in range(len(Col))]
                            generation_record[
                                Col.DSN.value] = self._base + '.' + fields[-1]
                            Log().logger.info(
                                '[gdg] Current generation being processed: ' +
                                generation_record[Col.DSN.value])

                            if fields[0] == 'Migrated':
                                fields = self._get_migrated(
                                    self._record, fields, i)

                            # New evaluation of len(fields) required after migrated update
                            if len(fields) == 0:
                                Log().logger.info(
                                    '[listcat] Fields still empty after recall')
                                status = 'FAILED'

                            elif len(fields) > 1:
                                status = 'SUCCESS'

                                if fields[1] == 'Tape':
                                    Log().logger.info(
                                        '[gdg] Generation in "Tape" volume')
                                    generation_record[
                                        Col.VOLSER.value] = fields[1]
                                elif len(fields) > 7:
                                    self._update_record(generation_record,
                                                        fields)
                                else:
                                    Log().logger.info(
                                        '[listcat] Scenario not supported')
                                    status = 'FAILED'

                            else:
                                Log().logger.info('[gdg] Fields incomplete')
                                status = 'FAILED'
                                failed = True

                            if status == 'SUCCESS':
                                Log().logger.debug(
                                    '[gdg] Adding new record for generation: ' +
                                    generation_record[Col.DSN.value])

                                new_record = DatasetRecord(Col)
                                new_record.columns = generation_record

                                self._generations_count += 1
                                Context().records.insert(
                                    self._index + self._generations_count,
                                    new_record)

                            Log().logger.info('LISTCAT GDG GENERATION ' +
                                              status)

                        elif fields[
                                -1] == 'Dsname' and self._generations_count > 0:
                            Log().logger.info('[gdg] Oldest generation reached')
                            status = 'SUCCESS'
                            rc = 0
                            break
                        elif fields[
                                -1] == 'Dsname' and self._generations_count == 0 and failed is False:
                            Log().logger.info(
                                '[gdg] No generation found for given GDG base')
                            status = 'SUCCESS'
                            rc = 0
                            break
                        elif fields[
                                -1] == 'Dsname' and self._generations_count == 0 and failed is True:
                            Log().logger.info(
                                '[gdg] Generations found but all dataset info retrievals failed'
                            )
                            status = 'FAILED'
                            rc = -1
                            break
                        else:
                            Log().logger.debug(
                                '[gdg] Dataset name pattern not supported: ' +
                                fields[-1])
                            Log().logger.debug('[gdg] Skipping generation')
                            continue
                    else:
                        Log().logger.info('[gdg] Fields empty')
                        continue

                    if self._generations_count >= Context().generations:
                        Log().logger.info(
                            '[gdg] Max number of generations reached')
                        status = 'SUCCESS'
                        rc = 0
                        break
            else:
                Log().logger.info('[gdg] FTP result empty')
                status = 'FAILED'
                rc = -1
        elif rc == -1:
            Log().logger.error('[listcat] FTPListcatError: No such dataset on Mainframe: ' + self._base)
            status = 'FAILED'
        else:
            status = 'FAILED'

        Log().logger.info('LISTCAT GDG ' + status)

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
