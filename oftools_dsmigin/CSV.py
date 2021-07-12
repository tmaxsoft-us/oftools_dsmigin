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
import datetime
import os
import shutil

# Third-party modules

# Owned modules
from .Context import Context
from .MigrationEnum import Col


class CSV():
    """A class used to manipulate the CSV file , read and write tasks but also backup and other smaller features.

    Attributes:
        _column_names: A list, the names of the different columns of the CSV file. 
        _work_directory: A string, working directory for the program execution.
        _file_path: A string, absolute path to the CSV file.
        _file_name: A string, the full name of the CSV file.
        _root_file_name: A string, the name of the CSV file without extension.
        _tag: A string, the tag option used by the user.
        _timestamp: A string, the date and time of execution of the program in a certain format.
        _records: A 2D-list, the elements of the CSV file containing all the dataset data.

    Methods:
        __init__(): Initializes all attributes.
        _check_column_headers(headers): Compare column headers in the CSV file to model in the program.
        read(): Read the content of the CSV file and store the result in a list.
        write(records): Write the changes on the dataset records to the CSV file.
        backup(): Create a backup of the CSV file in a dedicated directory under the work directory.
    """

    def __init__(self):
        """Initializes all attributes.
        """
        self._column_names = []
        for column in Col:
            self._column_names.append(column.name)

        self._work_directory = Context().get_work_directory()
        self._file_path = Context().get_input_csv()
        self._file_name = self._file_path.rsplit('/')[0]
        self._root_file_name = self._file_name.split('.')[0]
        self._tag = Context().get_tag()

        today = datetime.datetime.today()
        self._timestamp = today.strftime('%Y%m%d_%H%M%S')

        self._records = []

    def _check_column_headers(self, headers):
        """Compare column headers in the CSV file to model in the program.

        First, this method checks if the number of columns match, and then the name of the column headers. If that is not the case, it sends an error message and shows the program definition (columns model) to the user.

        Args:
            headers: A list, headers of the columns extracted from the file.

        Returns:
            An integer, the return code of the method.
        """
        rc = 0

        # If the number of columns in the CSV file does match the number of elements in _column_names
        if len(headers) == len(self._column_names):
            # The name of each column of the file has to match the name in the list _column_names
            for i in range(len(headers)):
                if headers[i].strip() != self._column_names:
                    rc = 1
                    break
        else:
            rc = 1

        if rc != 0:
            print(
                'Column names does not match with the program\nInput file:\n' +
                headers + '\nProgram definition:\n' + self._column_names)
            exit(-1)

        return rc

    def read(self):
        """Read the content of the CSV file an store the result in a list.

        First, this method opens the CSV file specified. Then, it checks that the CSV file is a dataset data file by checking the column headers of the file. It could be just the list of dataset names, or the full CSV file with all the columns filled. It saves the content of the CSV file to the list records. 

        Returns:
            A 2D-list, the datasets data extracted from the CSV file.
        """
        with open(self._file_path, 'r') as csvfile:
            csv_data = csv.reader(csvfile, delimiter=',')
            for i in range(len(csv_data)):
                if i == 0 and csv_data[i][0].strip() == Col.DSN.name:
                    print('List of dataset names only')
                    continue
                # Checking headers of the CSV file
                if i == 0 and csv_data[i][0].strip() == Col.DSN.name and len(csv_data[i]) > 1:
                    print('Fully qualified CSV file. Checking headers')
                    self._check_column_headers(csv_data[0])
                    continue

                # This is not the header of the file, saving the data
                record = []
                for element in csv_data[i]:
                    record.append(element)
                self._records.append(record)
                # Check that DSN is not missing
                if record[Col.DSN.value] in ('', ' ', None):
                    print('Missing dataset name (DSN) on the line ' + i)

        return self._records

    def write(self, records):
        """Write the changes on the dataset records to the CSV file.

        It just open the CSV file, write the first row with the headers and then write the data from the list records.

        Args:
            records: A 2D-list, dataset data after all the changes applied in the program execution.

        Returns:
            An integer, the return code of the method.
        """
        rc = 0
        self._records = records

        with open(self._file_path, 'w') as csvfile:
            csv_data = csv.writer(csvfile, delimiter=',')
            # Writing column headers to CSV file
            csv_data.writerow(self._column_names)

            # Writing data from records to CSV file
            for record in self._records:
                csv_data.writerow(record)

        return rc

    def backup(self):
        """Create a backup of the CSV file in a dedicated directory under the work directory.

        Pattern for backup file naming: name_tag_timestamp_bckp.csv. This method make sure that the backup folder already exist before creating the first backup. It then copy the CSV file file to the target directory.

        Returns:
            An integer, the return code of the method.
        """
        rc = 0
        # Naming convention for the backup files
        backup_directory = self._work_directory + '/csv_backups'
        backup_file_name = self._root_file_name + '_' + self._tag + '_' + self._timestamp + '_bckp.csv'

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