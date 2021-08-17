#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module that contains all functions required for an update of the CSV file for VSAM datasets.

    Typical usage example:
      listcat = Listcat()
      listcat.run(records)"""

# Generic/Built-in modules
import os

# Third-party modules

# Owned modules
from .Context import Context
from .Log import Log
from .MigrationEnum import Col
from .Utils import Utils


class Listcat(object):
    """A class to update certain fields in the CSV file regarding the VSAM datasets using the result of the comman listcat executed in the mainframe.

        Attributes:
            _listcat_list: A list, the name of the text file(s) that contains the listcat output.
            _listcat_result: A string, the data extracted from the listcat output file.
            _csv_records: A 2D-list, the elements of the CSV file containing all the dataset data.

        Methods:
            __init__(): Initialize all attributes.
            _read(): Read the content of the listcat output file and store the result in a string.
            _analyze(): Analyze the data extracted from the listcat output file.
            _update_csv_records(): Take the liscat extracted data to update the CSV records.
            run(records): Main method for listcat data retrieval."""

    def __init__(self):
        """Initialize all attributes.
            """
        self._file_path = Context().listcat_directory + '/listcat.txt'
        self._data = None

    def read(self):
        """Read the content of the listcat output file and store the result in a string.

            One listcat file can contains the info of one or multiple datasets.

            Args:
                listcat_file: A string, the absolute path of the file.

            Returns:
                A string, the data extracted from the listcat text file."""
        rc = 0
        try:
            with open(self._file_path, mode='r') as fd:
                self._data = fd.read()

            if self._data != None:
                Log().logger.debug('[listcat] Listcat file import successful')
                rc = 0
            else:
                Log().logger.error('[listcat] Listcat file import failed')
                rc = -1

        except FileNotFoundError:
            Log().logger.warning(
                '[listcat] FileNotFoundError: No such file or directory:' +
                self._file_path)
            rc = 1

        finally:
            return rc

    def get_data(self, record):
        """Analyze the data extracted from the listcat output file.

            Returns:
                A list, the listcat information correctly formatted and organized."""
        rc = 0
        flag = 0

        for line in self._data.splitlines():
            if flag == 0:
                if 'DATA ------- ' + record[Col.DSN.value] in line:
                    flag = 1
                    record[Col.RECFM.value] = 'VB'
            else:
                info_list = line.replace('-', '')
                info_list = info_list.split()

                for element in info_list:
                    if element.startswith('RKP'):
                        record[Col.KEYOFF.value] = element.replace('RKP', '')
                    elif element.startswith('KEYLEN'):
                        record[Col.KEYLEN.value] = element.replace('KEYLEN', '')
                    elif element.startswith('MAXLRECL'):
                        record[Col.MAXLRECL.value] = element.replace(
                            'MAXLRECL', '')
                    elif element.startswith('AVGLRECL'):
                        record[Col.AVGLRECL.value] = element.replace(
                            'AVGLRECL', '')
                    elif element.startswith('CISIZE'):
                        record[Col.CISIZE.value] = element.replace('CISIZE', '')
                    elif element.startswith('INDEXED'):
                        record[Col.VSAM.value] = 'KS'
                    #? How to identify VSAM datasets ES and RR?

                #TODO Trying to avoid reading useless lines down below
                if record[Col.KEYLEN.value] != '' and record[Col.VSAM.value] != '':
                    break
                if 'INDEX ------ ' + record[Col.DSN.value] in line:
                    break

        if rc == 0:
            status = 'SUCCESS'
        #TODO No way to fail this at the moment
        else:
            status = 'FAILED'

        Log().logger.info('LISTCAT FILE' + status)

        return rc

    def update_dataset_record(self, record):
        """Take the liscat extracted data to update the CSV records.

            It first update the CSV records with different data regarding the VSAM datasets, data required for a successful migration of this type of dataset. Then, it also look for each VSAM datasets if there are the equivalent 'INDEX and 'DATA'. These datasets are not useful for migration, so the tool removes them.

            Returns:
                A 2D-list, the updated dataset data with listcat information for VSAM datasets."""
        rc = 0

        if self._data != None:
            dsn_list = []
            records = Context().records
            for dataset_record in records:
                dsn_list.append(dataset_record.columns[Col.DSN.value])
            # dsn_list = [records.columns[Col.DSN.value] for _ in records]

            index_dsn = record[Col.DSN.value] + '.INDEX'
            if index_dsn in dsn_list:
                # Replace the value in the column named DSORG by VSAM in the records list
                record[Col.DSORG.value] = 'VSAM'
                # Identify the position of the index DSN in the dsn_list
                i = dsn_list.index(index_dsn)
                # Remove the line where this DSN appears in the records list
                Context().records.remove(Context().records[i])
                Log().logger.info(
                    'Removed from dataset list: ' + index_dsn +
                    '. This is not useful for migration to OpenFrame.')

            data_dsn = record[Col.DSN.value] + '.DATA'
            if data_dsn in dsn_list:
                record[Col.DSORG.value] = 'VSAM'
                # Identify the position of the data DSN in the dsn_list
                j = dsn_list.index(data_dsn)
                # Remove the line where this DSN appears in the records list
                Context().records.remove(Context().records[j])
                Log().logger.info(
                    '[LISTCAT] Removed from dataset list: ' + data_dsn +
                    '. This is not useful for migration to OpenFrame.')

        return rc
