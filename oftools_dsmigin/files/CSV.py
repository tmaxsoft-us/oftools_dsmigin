#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This modules runs all functions related to the CSV file.

Typical usage example:
  csv = CSV(csv_path)
  csv.write()
"""

# Generic/Built-in modules
import os
import sys

# Third-party modules

# Owned modules
from ..Context import Context
from ..DatasetRecord import DatasetRecord
from ..enums.MessageEnum import ErrorM, LogM
from ..enums.MigrationEnum import MCol, Width
from ..handlers.FileHandler import FileHandler
from ..Log import Log


class CSV(object):
    """A class used to manipulate the CSV file, read and write tasks but also backup and other smaller features.

    Attributes:
        _headers_definition {list} -- List to store the headers from the program definition.
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
        """Initializes the class with all the attributes.
        """
        self._headers_definition = [column.name for column in MCol]
        self._column_widths = [width.value for width in Width]

        self._file_path = os.path.expandvars(csv_path)
        self._file_path = os.path.abspath(self._file_path)

        self._file_name = self._file_path.rsplit('/', 1)[1]
        self._root_file_name = self._file_name.split('.')[0]

        self._headers_formatted = DatasetRecord(MCol)
        self._headers_formatted.columns = [column.name for column in MCol]
        self._headers_formatted = self._headers_formatted.format(
            self._column_widths)

        self._records_formatted = []

        if Context().initialization:
            self._create_file()
        else:
            self._read()
            self._backup()

    def _create_file(self):
        """
        """
        Log().logger.info(LogM.CSV_INIT.value % self._file_path)
        self.write()

    def _read(self):
        """Reads the content of the CSV file an store the data in a list.

        First, this method opens the CSV file specified. Then, it checks that the CSV file is a dataset data file by checking the column headers of the file. It could be just the list of dataset names, or the full CSV file with all the columns filled. It saves the content of the CSV file to the list Context().records.

        Raises:
            IndexError -- Exception is raised if there is too many elements in a given line.
            FileNotFoundError -- Exception is raised if the CSV file has not been found in the read_file execution and consequently needs to be initialized.
        """
        line_number = 0
        Log().logger.debug(LogM.CSV_READ.value % self._file_path)

        try:
            data = FileHandler().read_file(self._file_path)

            if data is not None:
                for line_number, line in enumerate(data):
                    if line_number == 0:
                        self._check_headers(line)
                    else:
                        record = DatasetRecord(MCol)
                        record.columns = line
                        Context().records.append(record)

                self._records_formatted = [
                    record.format(self._column_widths)
                    for record in Context().records
                ]
            else:
                raise FileNotFoundError()

        except IndexError:
            Log().logger.critical(ErrorM.INDEX_ELEMENTS_LINE.value % line_number)
            sys.exit(-1)
        except FileNotFoundError:
            Log().logger.critical(ErrorM.INIT.value %
                                  'dataset migration CSV file')
            sys.exit(-1)

    def _backup(self):
        """Creates a backup of the CSV file.

        Pattern for backup file naming: name_tag_timestamp.csv. This method copies the CSV file under the backup directory, which is under the working directory.

        Returns:
            integer -- Return code of the method.
        """
        Log().logger.debug(LogM.CSV_BACKUP.value % self._file_path)

        backup_file_name = self._root_file_name + Context().tag + '_' + Context(
        ).time_stamp('full') + '.csv'
        backup_file_path = Context(
        ).csv_backups_directory + '/' + backup_file_name

        rc = FileHandler().copy_file(self._file_path, backup_file_path)

        return rc

    def _check_headers(self, headers):
        """Compares column headers in the CSV file to a definition in the program.

        First, this method checks if the number of columns match, and then if the column headers match as well. If that is not the case, it sends an error message and shows the program definition to the user.

        Arguments:
            headers {list} -- Columns headers extracted from the CSV file.

        Raises:
            SystemError -- Exception is raised if there is typo on one of the headers.
        """
        issue_message = ''
        headers_definition = [column.name for column in MCol]

        if len(headers) < len(headers_definition):
            if len(headers) == 1:
                Log().logger.debug(LogM.HEADERS_DSN_ONLY.value)

            issue_message = 'Missing headers'
            rc = -1

        elif len(headers) > len(headers_definition):
            issue_message = 'Extra headers'
            rc = -1

        else:
            header_typos = list(set(headers) - set(headers_definition))

            if len(header_typos) == 0:
                rc = 0
            elif len(header_typos) == 1:
                issue_message = 'Typographical error on the header: ' + header_typos[
                    0]
                rc = -1
            else:
                issue_message = 'Typographical errors on the headers: ' + ', '.join(
                    header_typos)
                rc = -1

        if rc == -1:
            Log().logger.warning(ErrorM.HEADERS_WARNING.value % issue_message)
            Log().logger.info(LogM.HEADERS_FILE.value % ', '.join(headers))
            Log().logger.info(LogM.HEADERS_PROG.value % ', '.join(headers_definition))

            Log().logger.info(LogM.HEADERS_FIX.value)
            rc = 0
        else:
            Log().logger.debug(LogM.HEADERS_OK.value)

    def write(self, index=None):
        """Writes the dataset migration records to the CSV file.

        Updates the formatted records if any changes and then writes to the CSV file, the headers in the first row and then the migration records.

        Arguments:
            index {integer} -- Index of the record to be formatted.

        Returns:
            integer -- Return code of the method.
        """
        Log().logger.debug(LogM.CSV_WRITE.value % self._file_path)

        if index is not None:
            record = Context().records[index]
            self._records_formatted[index] = record.format(self._column_widths)

        content = [self._headers_formatted] + list(self._records_formatted)
        rc = FileHandler().write_file(self._file_path, content)

        return rc

    def add_records(self, args_dsn):
        """Add manual dataset input to the storage resource.

        Arguments:
            args_dsn {string} -- Dataset name manual input if any.
        """
        if args_dsn:
            dataset_names = args_dsn.split(':')
            for dsn in dataset_names:
                record = DatasetRecord(MCol)
                record.columns = [dsn]

                Context().records.append(record)
                self._records_formatted.append(
                    record.format(self._column_widths))
