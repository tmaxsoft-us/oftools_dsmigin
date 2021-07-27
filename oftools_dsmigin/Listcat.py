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
            _listcat_records: A 2D-list, the elements of the listcat result containing updates for VSAM datasets. 

        Methods:
            __init__(): Initialize all attributes.
            _read(): Read the content of the listcat output file and store the result in a string.
            _analyze(): Analyze the data extracted from the listcat output file.
            _update_csv_records(): Take the liscat extracted data to update the CSV records.
            run(records): Main method for listcat data retrieval."""

    def __init__(self):
        """Initialize all attributes.
            """
        self._file_path = os.path.expandvars(Context().listcat_file_path)
        self._file_path = os.path.abspath(self._file_path)
        self._file_name = self._file_path.rsplit('/', 1)[1]
        # Listcat file does not have any extension
        self._root_file_name = self._file_name

        self._data = None
        self._records = []

        self._backup()
        self._read()

    def _backup(self):
        """Creates a backup of the listcat file.

            Pattern for backup file naming: name_tag_timestamp_bckp.csv. This method make sure that the backup folder already exist before creating the first backup. It then copy the CSV file file to the target directory. Save the backup file in a dedicated directory under the working directory.
            # Naming convention for the backup files

            Returns:
                An integer, the return code of the method."""
        listcat_backup_file_path = Context(
        ).listcat_directory + self._root_file_name

        rc = Utils().copy_file(self._file_path, listcat_backup_file_path)

        return rc

    def _read(self):
        """Read the content of the listcat output file and store the result in a string.

            One listcat file can contains the info of one or multiple datasets.

            Args:
                listcat_file: A string, the absolute path of the file.

            Returns:
                A string, the data extracted from the listcat text file."""
        with open(self._file_path, mode='r') as fd:
            self._data = fd.read()

        if self._data != None:
            Log().logger.debug('[LISCAT] Listcat file successfully imported')

        return self._data

    def analyze(self):
        """Analyze the data extracted from the listcat output file.

            Returns:
                A list, the listcat information correctly formatted and organized."""
        rc = 0
        lines = self._data.splitlines()

        for i in range(len(lines)):
            fields = lines[i].split()
            # TODO update listcat result processing here
            if fields[0] == 'DSN':
                record = []
                recfm = lines[i + 1].split()[1]
                keyoff = lines[i + 2].split()[2]
                record.append(recfm, keyoff)

                self._records.append(record)

        return rc

    def update_dataset_records(self):
        """Take the liscat extracted data to update the CSV records.

            It first update the CSV records with different data regarding the VSAM datasets, data required for a successful migration of this type of dataset. Then, it also look for each VSAM datasets if there are the equivalent 'INDEX and 'DATA'. These datasets are not useful for migration, so the tool removes them.

            Returns:
                A 2D-list, the updated dataset data with listcat information for VSAM datasets."""
        rc = 0
        dataset_records = Context().records
        dsn_list = [
            dataset_records.columns[Col.DSN.value] for record in dataset_records
        ]

        for record in self._records:
            dsn = record[Col.DSN.value]

            if dsn in dsn_list:
                i = dsn_list.index(dsn)
                dataset_records[i].columns[Col.RECFM.value] = record[
                    Col.RECFM.value]
                dataset_records[i].columns[Col.KEYOFF.value] = record[
                    Col.KEYOFF.value]
                dataset_records[i].columns[Col.KEYLEN.value] = record[
                    Col.KEYLEN.value]
                dataset_records[i].columns[Col.MAXLRECL.value] = record[
                    Col.MAXLRECL.value]
                dataset_records[i].columns[Col.AVGLRECL.value] = record[
                    Col.AVGLRECL.value]
                dataset_records[i].columns[Col.CISIZE.value] = record[
                    Col.CISIZE.value]
                if record[Col.CISIZE.value] == 'INDEXED':
                    dataset_records[i][Col.VSAM.value] = 'KS'
                # TODO Finish the update of the fields

            index_dsn = dsn + '.INDEX'
            if index_dsn in dsn_list:
                # Replace the value in the column named DSORG by VSAM in the records list
                dataset_records.columns[i][Col.DSORG.value] = 'VSAM'
                # Identify the position of the index DSN in the dsn_list
                j = dsn_list.index(index_dsn)
                # Remove the line where this DSN appears in the records list
                dataset_records.remove(dataset_records[j])
                Log().logger.info(
                    'Removed from dataset list: ' + index_dsn +
                    '. This is not useful for migration to OpenFrame.')

            data_dsn = dsn + '.DATA'
            if data_dsn in dsn_list:
                dataset_records.columns[i][Col.DSORG.value] = 'VSAM'
                # Identify the position of the data DSN in the dsn_list
                k = dsn_list.index(data_dsn)
                # Remove the line where this DSN appears in the records list
                dataset_records.remove(dataset_records[k])
                Log().logger.info(
                    '[LISTCAT] Removed from dataset list: ' + data_dsn +
                    '. This is not useful for migration to OpenFrame.')

        return rc
