#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This modules runs all functions related to the CSV file.

    Typical usage example:
      csv = CSV(csv_path)
      csv.backup()
      csv.read()
      csv.write()
"""

# Generic/Built-in modules
import csv
import os
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
        self._headers = [column.name for column in Col]

        self._file_path = os.path.expandvars(csv_path)
        self._file_path = os.path.abspath(self._file_path)

        file_name = self._file_path.rsplit('/', 1)[1]
        self._root_file_name = file_name.split('.')[0]

        self._data = None

        self._read()

    def _read(self):
        """Reads the content of the CSV file an store the data in a list.

            First, this method opens the CSV file specified. Then, it checks that the CSV file is a dataset data file by checking the column headers of the file. It could be just the list of dataset names, or the full CSV file with all the columns filled. It saves the content of the CSV file to the list records. 

            Returns:
                A 2D-list, the datasets data extracted from the CSV file."""

        rc = 0

        try:
            if os.path.isfile(self._file_path):
                self._backup()
                self._data = Utils().read_file(self._file_path)

                if self._data != None:
                    for i in range(len(self._data)):
                        if i == 0:
                            rc = self._check_headers(self._data[i])
                        else:
                            record = DatasetRecord()
                            record.columns = self._data[i]
                            Context().records.append(record)

            else:
                raise FileNotFoundError()

        except FileNotFoundError:
            Log().logger.info('FileNotFoundError: No such file or directory: ' +
                              self._file_path)
            Log().logger.info('Creating CSV file from template')
            self.write()

        finally:
            return rc

    def _backup(self):
        """Creates a backup of the CSV file.

            Pattern for backup file naming: name_tag_timestamp_bckp.csv. This method make sure that the backup folder already exist before creating the first backup. It then copy the CSV file file to the target directory. Save the backup file in a dedicated directory under the working directory.
            # Naming convention for the backup files

            Returns:
                An integer, the return code of the method."""
        backup_file_name = self._root_file_name + Context().tag + '_' + Context(
        ).full_timestamp + '.csv'
        backup_file_path = Context(
        ).csv_backup_directory + '/' + backup_file_name

        rc = Utils().copy_file(self._file_path, backup_file_path)

        return rc

    def _check_headers(self, headers):
        """Compares column headers in the CSV file to model in the program.

            First, this method checks if the number of columns match, and then if the column headers match as well. If that is not the case, it sends an error message and shows the program definition (column headers model) to the user.

            Args:
                headers: A list, headers of the columns extracted from the file.

            Returns:
                An integer, the return code of the method."""
        if len(headers) == 1:
            Log().logger.debug('[csv] List of dataset names only')
            rc = 1
        elif len(headers) < len(self._headers):
            Log().logger.error('[csv] Missing headers')
            rc = -1
        elif len(headers) == len(self._headers):
            for i in range(len(headers)):
                header = headers[i].strip()
                if header == self._headers[i]:
                    rc = 0
                else:
                    Log().logger.error(
                        '[csv] Typographical error on the header: ' + header)
                    rc = -1
                    break
        else:
            Log().logger.error('[csv] Too many headers specified')
            rc = -1

        if rc == 0:
            Log().logger.debug('[csv] Headers correctly specified')
        elif rc < 0:
            Log().logger.error(
                '[csv] Headers are not matching with the program definition')
            Log().logger.error('[csv] Input file:')
            Log().logger.error(headers)
            Log().logger.error('[csv] Program definition:')
            Log().logger.error(self._headers)
            sys.exit(-1)

        return rc

    def write(self):
        """Write the changes on the dataset records to the CSV file.

            Opens the CSV file, writes the headers in the first row and then writes the data from the records.

            Args:
                records: A 2D-list, dataset data after all the changes applied in the program execution.

            Returns:
                An integer, the return code of the method."""
        rc = 0

        with open(self._file_path, 'w') as fd:
            csv_data = csv.writer(fd, delimiter=',')
            # Writing column headers to CSV file
            rc = csv_data.writerow(self._headers)
            # Log().logger.debug(
            #     '[csv] Return code of the call to the write method for the headers:'
            #     + str(rc))

            # Writing records to CSV file
            for record in Context().records:
                rc = csv_data.writerow(record.columns)
                # Log().logger.debug(
                #     '[csv] Return code of the call to the write method for the data:'
                #     + str(rc))
            #TODO Need a performance test
            # rc = csv_data.writerows(Context().records)

        return rc