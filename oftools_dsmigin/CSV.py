#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""This modules runs all functions related to the CSV file.

Typical usage example:
    csv_file = CSV()
    csv_file.read()
    csv_file.write(records)
    csv_file.backup()
"""

# Generic/Built-in modules
import csv
import os
import shutil
import sys

# Third-party modules

# Owned modules
from .Context import Context
from .DatasetRecord import DatasetRecord
from .Log import Log
from .MigrationEnum import Col
from .Utils import Utils


class CSV(object):
    """A class used to manipulate the CSV file , read and write tasks but also backup and other smaller features.

        Attributes:
            _column_names: A list, the names of the different columns of the CSV file. 
            _work_directory: A string, working directory for the program execution.
            _file_path: A string, absolute path to the CSV file.
            _file_name: A string, the full name of the CSV file.
            _root_file_name: A string, the name of the CSV file without extension.
            _timestamp: A string, the date and time of execution of the program in a certain format.
            _records: A 2D-list, the elements of the CSV file containing all the dataset data.

        Methods:
            __init__(): Initializes all attributes.
            _check_column_headers(headers): Compare column headers in the CSV file to model in the program.
            read(): Read the content of the CSV file and store the result in a list.
            write(records): Write the changes on the dataset records to the CSV file.
            backup(): Create a backup of the CSV file in a dedicated directory under the work directory."""

    def __init__(self, csv_path):
        """Initializes all attributes.
            """
        self._column_names = []
        for column in Col:
            self._column_names.append(column.name)

        self._data = Utils().read_file(csv_path)
        self._file_path = os.path.abspath(csv_path)
        self._file_name = self._file_path.rsplit('/', 1)[1]
        self._root_file_name = self._file_name.split('.')[0]

        self._backup()
        self._read()

    def _check_column_headers(self, headers):
        """Compare column headers in the CSV file to model in the program.

            First, this method checks if the number of columns match, and then the name of the column headers. If that is not the case, it sends an error message and shows the program definition (columns model) to the user.

            Args:
                headers: A list, headers of the columns extracted from the file.

            Returns:
                An integer, the return code of the method."""
        rc = 0
        # If the number of columns in the CSV file does match the number of elements in _column_names
        if len(headers) == len(self._column_names):
            # The name of each column of the file has to match the name in the list _column_names
            for i in range(len(headers)):
                if headers[i].strip() != self._column_names[i]:
                    rc = -1
                    break
        else:
            rc = -1

        if rc != 0:
            Log().logger.error(
                '[CSV] Column names are not matching with the program definition'
            )
            Log().logger.error('Input file:')
            Log().logger.error(headers)
            Log().logger.error('Program definition:')
            Log().logger.error(self._column_names)
            sys.exit(-1)

        return rc

    def _read(self):
        """Read the content of the CSV file an store the result in a list.

            First, this method opens the CSV file specified. Then, it checks that the CSV file is a dataset data file by checking the column headers of the file. It could be just the list of dataset names, or the full CSV file with all the columns filled. It saves the content of the CSV file to the list records. 

            Returns:
                A 2D-list, the datasets data extracted from the CSV file."""
        rc = 0

        for i in range(len(self._data)):
            if i == 0 and self._data[i][0].strip() == Col.DSN.name:
                Log().logger.debug('[CSV] List of dataset names only')
                continue
            # Checking headers of the CSV file
            if i == 0 and self._data[i][0].strip() == Col.DSN.name and len(
                    self._data[i]) > 1:
                Log().logger.debug(
                    '[CSV] Fully qualified CSV file. Checking headers')
                self._check_column_headers(self._data[0])
                continue

            # This is not the header of the file, saving the data
            record = DatasetRecord()
            record.columns = self._data[i]
            Context().records.append(record)
            # Check that DSN is not missing
            if record.columns[Col.DSN.value] in ('', ' ', None):
                print('Missing dataset name (DSN) on the line ' + i)

        return rc

    def write(self):
        """Write the changes on the dataset records to the CSV file.

            It just open the CSV file, write the first row with the headers and then write the data from the list records.

            Args:
                records: A 2D-list, dataset data after all the changes applied in the program execution.

            Returns:
                An integer, the return code of the method."""
        rc = 0

        with open(self._file_path, 'w') as csvfile:
            csv_data = csv.writer(csvfile, delimiter=',')
            # Writing column headers to CSV file
            csv_data.writerow(self._column_names)

            # Writing data from records to CSV file
            #TODO Find a way (maybe) to write only the changes, and not all the rows every single time
            for record in Context().records:
                csv_data.writerow(record)

        return rc

    def _backup(self):
        """Create a backup of the CSV file in a dedicated directory under the work directory.

            Pattern for backup file naming: name_tag_timestamp_bckp.csv. This method make sure that the backup folder already exist before creating the first backup. It then copy the CSV file file to the target directory.

            Returns:
                An integer, the return code of the method."""
        rc = 0
        # Naming convention for the backup files
        backup_directory = Context().working_directory + '/csv_backups'
        backup_file_name = self._root_file_name + '_' + Context(
        ).tag + '_' + Context().timestamp + '_bckp.csv'

        try:
            # Create the backup directory if it does not exist already
            if not os.path.exists(backup_directory):
                os.mkdirs(backup_directory)
        except:
            print('CSV backup directory creation failed. Permission denied.')

        backup_file_path = backup_directory + backup_file_name
        try:
            # Copy the CSV file to a backup file
            shutil.copy(self._file_path, backup_file_path)
        except:
            print('CSV backup file creation failed. Permission denied.')

        return rc