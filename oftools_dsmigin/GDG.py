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
            _record {list} -- The given migration record containing dataset info.
            _base {string} -- GDG base name.
            _generations {2D-list} -- The FTP command output, one element of the list being one line, one line corresponding to one dataset info.
            
        Methods:
            __init__(record) -- Initializes all attributes of the class.
            _recall(dataset_name) -- Executes FTP command to make dataset available to download.
            _get_migrated(record, fields, line_number) -- Executes the FTP command on Mainframe to retrieve dataset info in the case where VOLSER is set to Migrated.
            _update_record(fields, record) -- Updates migration dataset record with parameters extracted from the FTP command output.
            get_dataset_records() -- Performs all the steps to exploit Mainframe info for GDG datasets only, and updates the migration records accordingly.
    """

    def __init__(self, record):
        """Initializes all attributes of the class.
        """
        self._record = record
        self._base = record[Col.DSN.value]

        self._generations = []

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
                list --
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
            if len(self._generations) > 0:
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

        generations_count = 0

        if rc == 0:
            self._generations = stdout.splitlines()
            if len(self._generations) > 0:

                for i in range(len(self._generations) - 1, -1, -1):
                    fields = self._generations[i].split()
                    if len(fields) > 0:
                        if bool(re.match(r"G[0-9]{4}V[0-9]{2}", fields[-1])):

                            # Latest generation
                            if generations_count == 0:
                                self._record[Col.DSN.value] += '.' + fields[-1]
                                Log().logger.debug(
                                    '[gdg] Current generation being processed: '
                                    + self._record[Col.DSN.value])

                                if fields[0] == 'Migrated':
                                    fields = self._get_migrated(
                                        self._record, fields, i)

                                if len(fields) > 7:
                                    self._update_record(fields, self._record)
                                    status = 'SUCCESS'
                                else:
                                    Log().logger.debug(
                                        '[gdg] Fields incomplete to get data')
                                    status = 'FAILED'

                                Log().logger.debug(
                                    'LISTCAT GDG LATEST GENERATION ' + status)
                                generations_count += 1

                            # Older generations
                            else:
                                generation_record = [
                                    '' for _ in range(len(Col))
                                ]
                                generation_record[
                                    Col.DSN.
                                    value] = self._base + '.' + fields[-1]
                                Log().logger.debug(
                                    '[gdg] Current generation being processed: '
                                    + generation_record[Col.DSN.value])

                                if fields[0] == 'Migrated':
                                    fields = self._get_migrated(
                                        generation_record, fields, i)

                                if len(fields) > 7:
                                    self._update_record(fields,
                                                        generation_record)
                                    new_record = DatasetRecord(Col)
                                    new_record.columns = generation_record
                                    Log().logger.debug(
                                        '[gdg] Adding new record for older generation: '
                                        + generation_record[Col.DSN.value])
                                    Context().records.append(new_record)
                                    status = 'SUCCESS'
                                else:
                                    Log().logger.debug(
                                        '[gdg] Fields incomplete to get data')
                                    status = 'FAILED'

                                Log().logger.debug(
                                    'LISTCAT GDG OLDER GENERATIONS ' + status)
                                generations_count += 1

                        elif fields[-1] == 'Dsname':
                            Log().logger.info('[gdg] Oldest generation reached')
                            status = 'SUCCESS'
                            rc = 0
                            break
                        else:
                            Log().logger.debug(
                                '[gdg] Dataset name pattern incorrect: ' +
                                fields[-1])
                            Log().logger.debug('[gdg] Skipping generation')
                            continue
                    else:
                        Log().logger.debug('[gdg] Fields empty')
                        continue

                    if generations_count >= Context().generations:
                        Log().logger.info(
                            '[gdg] Max number of generations reached')
                        rc = 0
                        break
            else:
                Log().logger.debug('[gdg] FTP result empty')
                status = 'FAILED'
                rc = -1
        else:
            status = 'FAILED'

        Log().logger.debug('LISTCAT GDG ' + status)

        return rc
