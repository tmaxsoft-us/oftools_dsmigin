#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run all tasks related to the CSV file.

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
from ..enums.CSV import MCol, Width
from ..enums.Message import ErrorM, LogM
from ..handlers.FileHandler import FileHandler
from ..Log import Log
from ..Record import Record


class CSV():
    """Manipulate the CSV file, like read and write tasks but also backup and
    other smaller features.

    Attributes:
        _headers_definition {list} -- List to store the headers from the
            program definition.
        _columns_widths {list} -- List to store the width of each column of the
            CSV file.

        _file_path {string} -- Absolute path of the CSV file.
        _file_name {string} -- Name of the CSV file.
        _root_file_name {string} -- Name of the CSV file, excluding extension.

        _headers_formatted {list} --

    Methods:
        __init__(csv_path) -- Initialize the class with its attributes.
        _create_file() -- Create the CSV file when the user specifies the
            --init flag.
        _backup() -- Create a backup of the CSV file.
        _read() -- Read the content of the CSV file and store the result in a
            list.
        _check_headers(headers) -- Compare column headers in the CSV file to the
            reference.
        write() -- Write the records to the CSV file.
        add_records(args_dsn) -- Add manual dataset input to the records list.
    """

    def __init__(self, csv_path):
        """Initialize the class with all the attributes.
        """
        self._column_widths = [width.value for width in Width]

        self._headers_formatted = Record(MCol)
        self._headers_formatted.columns = [column.name for column in MCol]
        self._headers_formatted = self._headers_formatted.format(
            self._column_widths)

        self._file_path = os.path.expandvars(csv_path)
        self._file_path = os.path.abspath(self._file_path)

        self._file_name = self._file_path.rsplit("/", 1)[1]
        self._root_file_name = self._file_name.split(".")[0]

        self._records_formatted = []

        if Context().initialization:
            self._create_file()
        else:
            self._backup()
            self._read()

    def _create_file(self):
        """Create the CSV file when the user specifies the --init flag.
        """
        Log().logger.info(LogM.CSV_INIT.value % self._file_path)
        self.write()

    def _backup(self):
        """Create a backup of the CSV file.

        Pattern for backup file naming: name_tag_timestamp.csv. This method
        copies the CSV file under the backup directory, which is under the
        working directory.

        Returns:
            integer -- Return code of the method.
        """
        Log().logger.debug(LogM.CSV_BACKUP.value % self._file_path)

        backup_file_name = self._root_file_name + Context().tag + "_" + Context(
        ).time_stamp("full") + ".csv"
        backup_file_path = Context(
        ).csv_backups_directory + "/" + backup_file_name

        status = FileHandler().copy_file(self._file_path, backup_file_path)

        return status

    def _read(self):
        """Read the content of the CSV file an store the data in a list.

        First, open the CSV file specified. Then, check that the CSV file is a
        dataset data file by checking the column headers of the file. It could
        be just the list of dataset names, or the full CSV file with all the
        columns filled. Finally, save the content of the CSV file to the list
        Context().records.

        Raises:
            IndexError -- Exception is raised if there is too many elements in
                a given line.
            FileNotFoundError -- Exception is raised if the CSV file has not
                been found in the read_file execution and consequently needs to
                be initialized.
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
                        record = Record(MCol)
                        record.columns = line
                        Context().records.append(record)

                self._records_formatted = [
                    record.format(self._column_widths)
                    for record in Context().records
                ]
            else:
                raise FileNotFoundError()

        except IndexError:
            Log().logger.critical(ErrorM.INDEX_ELEMENTS_LINE.value %
                                  line_number)
            sys.exit(-1)
        except FileNotFoundError:
            Log().logger.critical(ErrorM.INIT.value %
                                  "dataset migration CSV file")
            sys.exit(-1)

    def _check_headers(self, headers):
        """Compare column headers in the CSV file to the reference.

        First, check if the number of columns match, and then if the column
        headers match as well. If that is not the case, it will send an error
        message and shows the program definition to the user.

        Arguments:
            headers {list} -- Column headers extracted from the CSV file.

        Returns:
            integer - Return code of the method.
        """
        issue_message = ""
        headers_definition = [column.name for column in MCol]

        if len(headers) < len(headers_definition):
            if len(headers) == 1:
                Log().logger.debug(LogM.HEADERS_DSN_ONLY.value)

            issue_message = "Missing headers"
            status = -1

        elif len(headers) > len(headers_definition):
            issue_message = "Extra headers"
            status = -1

        else:
            header_typos = list(set(headers) - set(headers_definition))

            if len(header_typos) == 0:
                status = 0
            elif len(header_typos) == 1:
                issue_message = "Typographical error on the header: " + header_typos[
                    0]
                status = -1
            else:
                issue_message = "Typographical errors on the headers: " + ", ".join(
                    header_typos)
                status = -1

        if status == -1:
            Log().logger.warning(ErrorM.HEADERS_WARNING.value % issue_message)
            Log().logger.info(LogM.HEADERS_FILE.value % ", ".join(headers))
            Log().logger.info(LogM.HEADERS_PROG.value %
                              ", ".join(headers_definition))

            Log().logger.info(LogM.HEADERS_FIX.value)
            status = 0
        else:
            Log().logger.debug(LogM.HEADERS_OK.value)

        return status

    def write(self, index=None):
        """Writes the records to the CSV file.

        Format the updated record if any changes and then write to the CSV
        file, the headers in the first row and then the dataset migration
        records.

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
        status = FileHandler().write_file(self._file_path, content)

        return status

    def add_records(self, args_dsn):
        """Add manual dataset input to the records list.

        Arguments:
            args_dsn {string} -- Dataset name manual input if any.
        """
        if args_dsn:
            dataset_names = args_dsn.split(":")
            for dsn in dataset_names:
                record = Record(MCol)
                record.columns = [dsn]

                Context().records.append(record)
                self._records_formatted.append(
                    record.format(self._column_widths))
