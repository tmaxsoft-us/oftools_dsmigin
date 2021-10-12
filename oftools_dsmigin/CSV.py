#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This modules runs all functions related to the CSV file.

    Typical usage example:
        csv = CSV(csv_path)
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
from .MigrationEnum import Col, Width
from .Utils import Utils


class CSV(object):
    """A class used to manipulate the CSV file , read and write tasks but also backup and other smaller features.

        Attributes:
            _headers_definition {list} -- List to store the headers from the program definition.
            _headers_current {list} -- List to store the current status of the headers, extracted from the CSV file.
            _columns_widths {list} -- List to store the width of each column of the CSV file.
 
            _file_path {string} -- Absolute path to the CSV file.
            _root_file_name {string} -- Name of the CSV file, excluding extension.

        Methods:
            __init__(csv_path) -- Initializes all attributes of the class.
            _read() -- Reads the content of the CSV file and store the result in a list.
            _backup() -- Creates a backup of the CSV file.
            _check_column_headers(headers) -- Compares column headers in the CSV file to a definition in the program.
            _update_columns(update_type, record) -- Add or remove columns from each dataset migration record.
            write() -- Writes the dataset migration records changes to the CSV file.
            format() --Format CSV columns adding trailing spaces.
        """

    def __init__(self, csv_path):
        """Initializes all attributes of the class.
            """
        self._headers_definition = [column.name for column in Col]
        self._headers_current = []

        self._column_widths = [width.value for width in Width]

        self._file_path = os.path.expandvars(csv_path)
        self._file_path = os.path.abspath(self._file_path)

        file_name = self._file_path.rsplit('/', 1)[1]
        self._root_file_name = file_name.split('.')[0]

        self._read()

    def _read(self):
        """Reads the content of the CSV file an store the data in a list.

            First, this method opens the CSV file specified. Then, it checks that the CSV file is a dataset data file by checking the column headers of the file. It could be just the list of dataset names, or the full CSV file with all the columns filled. It saves the content of the CSV file to the list Context().records. 

            Returns:
                integer -- Return code of the method.
            
            Raises:
                IndexError -- Exception is raised if there is too many elements in a given line.
                IsADirectoryError -- Exception is raised if the given CSV is not a file but a directory.
                FileNotFoundError -- Exception is raised if the CSV file is not found at the given location.
            """
        rc = 0

        try:
            if Context().initialization:
                Log().logger.info('[csv] Initializing file from template')
                self.write()
            else:
                if os.path.isfile(self._file_path):
                    self._backup()
                    data = Utils().read_file(self._file_path)

                    if data != None:
                        for i in range(len(data)):
                            if i == 0:
                                rc = self._check_headers(data[i])
                            else:
                                if rc != 0:
                                    self._update_columns(rc, data[i])

                                record = DatasetRecord(Col)
                                record.columns = data[i]
                                Context().records.append(record)
                else:
                    if os.path.isdir(self._file_path):
                        raise IsADirectoryError()
                    else:
                        raise FileNotFoundError()

        except IndexError:
            Log().logger.error(
                'IndexError: Too many elements in the line number ' + str(i) +
                ' of the CSV file')
            sys.exit(-1)
        except IsADirectoryError:
            Log().logger.error(
                'IsADirectoryError: CSV specified is a directory: ' +
                self._file_path)
            sys.exit(-1)
        except FileNotFoundError:
            Log().logger.error(
                'FileNotFoundError: No such file or directory: ' +
                self._file_path)
            Log().logger.error(
                '[csv] Please initialize dataset migration CSV file with --init option'
            )
            sys.exit(-1)

        else:
            return rc

    def _backup(self):
        """Creates a backup of the CSV file.

            Pattern for backup file naming: name_tag_timestamp_bckp.csv. This method copies the CSV file under the backup directory, which is under the working directory.

            Returns:
                integer -- Return code of the method.
            """
        backup_file_name = self._root_file_name + Context().tag + '_' + Context(
        ).full_timestamp + '.csv'
        backup_file_path = Context(
        ).csv_backups_directory + '/' + backup_file_name

        rc = Utils().copy_file(self._file_path, backup_file_path)

        return rc

    def _check_headers(self, headers):
        """Compares column headers in the CSV file to a definition in the program.

            First, this method checks if the number of columns match, and then if the column headers match as well. If that is not the case, it sends an error message and shows the program definition to the user.

            Arguments:
                headers {list} -- Columns headers extracted from the CSV file.

            Returns:
                integer -- Return code of the method.
                
            Raises:
                SystemError -- Exception is raised if there is typo on one of the headers.
            """
        try:
            if len(headers) == 1:
                Log().logger.debug('[csv] List of dataset names only')
                rc = 0
            elif len(headers) < len(self._headers_definition):
                issue_message = 'Missing headers'
                self._headers_current = headers
                rc = 1
            elif len(headers) == len(self._headers_definition):
                for i in range(len(headers)):
                    header = headers[i].strip()
                    if header == self._headers_definition[i]:
                        rc = 0
                    else:
                        issue_message = 'Typographical error on the header: ' + header
                        rc = -1
                        break
            else:
                issue_message = 'Extra headers'
                self._headers_current = headers
                rc = 2

            if rc != 0:
                Log().logger.warning(
                    '[csv] Headers are not matching with the program definition: '
                    + issue_message)
                if rc == -1:
                    raise SystemError()
            else:
                Log().logger.debug('[csv] Headers correctly specified')

        except SystemError:
            Log().logger.error('[csv] Input file:')
            Log().logger.error(headers)
            Log().logger.error('[csv] Program definition:')
            Log().logger.error(self._headers_definition)
            sys.exit(-1)

        else:
            return rc

    def _update_columns(self, update_type, record):
        """Add or remove columns from each dataset migration record.

            Arguments:
                update_type {integer} -- Number to know if the CSV file needs more or less headers.
                record {list} -- CSV record currently being processed.
            """
        diff_headers = list(
            set(self._headers_definition) - set(self._headers_current))

        for header in diff_headers:
            # Missing headers
            if update_type == 1:
                Log().logger.info('[csv] Updating columns: Adding ' + header)
                index = self._headers_definition.index(header)
                record.insert(index, '')
            # Extra headers
            elif update_type == 2:
                Log().logger.info('[csv] Updating columns: Removing ' + header)
                index = self._headers_current.index(header)
                record.pop(index)

    def write(self):
        """Writes the dataset migration records changes to the CSV file.

            Opens the CSV file, writes the headers in the first row and then writes the data from the records.

            Returns:
                integer -- Return code of the method.
                
            Raises:
                OSError -- Exception is raised if there is an issue finding or opening the file.
            """
        try:
            with open(self._file_path, 'w') as fd:
                csv_data = csv.writer(fd, delimiter=',')
                # Writing column headers to CSV file
                csv_data.writerow(self._headers_definition)

                # Writing records to CSV file
                for record in Context().records:
                    csv_data.writerow(record.columns)
                #TODO Need a performance test
                # rc = csv_data.writerows(Context().records)
            rc = 0
        except OSError as e:
            Log().logger.error('OSError: ' + str(e))
            rc = -1

        return rc

    def format(self):
        """Format CSV columns adding trailing spaces.

            To ease reading and analyzing the file the columns are properly aligned based on an enumeration listing the width for each column.

            Raises:
                OSError -- Exception is raised if there is an issue finding or opening the file.
            """
        try:
            with open(self._file_path, 'w') as fd:
                csv_data = csv.writer(fd, delimiter=',')

                # Formatting column headers in CSV file
                Log().logger.debug(
                    '[csv] Formatting file: Adding trailing spaces to headers')
                for i in range(len(self._headers_definition)):
                    if len(self._headers_definition[i]
                          ) < self._column_widths[i]:
                        self._headers_definition[i] = self._headers_definition[
                            i].ljust(self._column_widths[i])
                csv_data.writerow(self._headers_definition)

                # Formatting records in CSV file
                Log().logger.debug(
                    '[csv] Formatting file: Adding trailing spaces to records')
                for dataset_record in Context().records:
                    record = dataset_record.columns
                    for i in range(len(record)):
                        if len(record[i]) < self._column_widths[i]:
                            record[i] = record[i].ljust(self._column_widths[i])
                    csv_data.writerow(record)
            rc = 0
        except OSError as e:
            Log().logger.error('OSError: ' + str(e))
            rc = -1

        return rc