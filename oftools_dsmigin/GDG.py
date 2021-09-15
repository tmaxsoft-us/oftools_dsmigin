#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Module .

    Typical usage example:
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .Context import Context
from .DatasetRecord import DatasetRecord
from .Log import Log
from .MigrationEnum import Col
from .Utils import Utils


class GDG():
    """
    """

    def __init__(self, record):
        """
        """
        self._record = record
        self._base = record[Col.DSN.value]
        self._shift = Context().generations + 2

        self._generations = []

    def _recall(self, dataset_name):
        """Executes FTP command to make dataset available to download.

            If a dataset has 'Migrated' as VOLSER parameter, the program executes this recall method just to open the diretory containing the dataset to trigger download execution from the mainframe.

            Args:
                record: A list, the dataset data to execute the recall using the DSN.

            Returns:
                An integer, the return code of the method."""
        Log().logger.info('[listcat] Recalling migrated dataset: ' +
                          dataset_name)
        ftp_command = 'cd ' + dataset_name
        Log().logger.debug('[listcat] ' + ftp_command)
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _get_migrated(self, record, fields, line_number):
        """
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

    def _update_record(self, fields, record):
        """
        """
        record[Col.RECFM.value] = fields[-5]
        record[Col.LRECL.value] = fields[-4]
        record[Col.BLKSIZE.value] = fields[-3]
        record[Col.DSORG.value] = fields[-2]
        record[Col.VOLSER.value] = fields[0]

    def _get_latest_generation(self):
        """
        """
        Log().logger.debug('[gdg] Getting latest generation for the dataset: ' +
                           self._base)
        ftp_command = 'cd ' + self._record[Col.DSN.value] + '\nls'
        Log().logger.debug('[gdg] ' + ftp_command)
        stdout, _, rc = Utils().execute_ftp_command(ftp_command)

        if rc == 0:
            self._generations = stdout.splitlines()
            if len(self._generations) > 0:
                fields = self._generations[-1].split()

                if len(fields) > 0:
                    #TODO Change to pattern identification: G0000V00
                    if fields[-1] == 'SAVED':
                        Log().logger.debug('[gdg] SAVED dataset: Skipping')
                        fields = self._generations[-2].split()
                        self._shift += 1

                    self._record[Col.DSN.value] += '.' + fields[-1]

                    if fields[0] == 'Migrated':
                        fields = self._get_migrated(self._record, fields, -1)

                    if len(fields) > 7:
                        self._update_record(fields, self._record)
                        status = 'SUCCESS'
                    else:
                        Log().logger.debug('[gdg] Fields incomplete to get data')
                        status = 'FAILED'
                else:
                    Log().logger.debug('[gdg] Fields empty')
                    status = 'FAILED'
            else:
                Log().logger.debug('[gdg] FTP result empty')
                status = 'FAILED'
        else:
            status = 'FAILED'

        Log().logger.info('LISTCAT GDG LATEST GENERATION ' + status)

        return rc

    def _get_older_generations(self):
        """
        """
        rc = 0

        if len(self._generations) > 1:
            Log().logger.debug('[gdg] Getting ' + Context().generations +
                               ' older generations for the dataset: ' +
                               self._base)

            for i in range(Context().generations, 1, -1):
                j = i - self._shift
                fields = self._generations[j].split()
                if len(fields) > 0:
                    if fields[-1].startswith('G'):
                        generation_record = ['' for _ in range(len(Col))]
                        generation_record[
                            Col.DSN.value] = self._base + '.' + fields[-1]
                        Log().logger.debug(
                            '[gdg] Current generation being processed: ' +
                            generation_record[Col.DSN.value])

                        if fields[0] == 'Migrated':
                            fields = self._get_migrated(generation_record, fields,
                                                        j)

                        if len(fields) > 7:
                            self._update_record(fields, generation_record)
                            new_record = DatasetRecord()
                            new_record.columns = generation_record
                            Log().logger.debug(
                                '[gdg] Adding new record for older generation: ' +
                                generation_record[Col.DSN.value])
                            Context().records.append(new_record)
                            status = 'SUCCESS'
                            rc = 0
                        else:
                            Log().logger.debug('[gdg] Fields incomplete to get data')
                            status = 'FAILED'
                            rc = -1
                    else:
                        Log().logger.info('[gdg] Latest generation reached')
                        rc = 0
                        break
                else:
                    Log().logger.debug('[gdg] Fields empty')
                    status = 'FAILED'
                    rc = -1
        else:
            Log().logger.debug('[gdg] FTP result empty')
            status = 'FAILED'
            rc = -1

        Log().logger.info('LISTCAT GDG OLDER GENERATIONS ' + status)

        return rc

    def get_dataset_records(self):
        """
        """
        self._get_latest_generation()

        if Context().generations > 0:
            self._get_older_generations()
