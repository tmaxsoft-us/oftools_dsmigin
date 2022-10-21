#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run all tasks to update the CSV file, specifically VSAM datasets.

Typical usage example:
  listcat = Listcat()
  listcat.run(records)
"""

# Generic/Built-in modules
import collections

# Third-party modules

# Owned modules
from ..Context import Context
from ..enums.Message import Color, LogM
from ..enums.CSV import LCol
from ..handlers.FileHandler import FileHandler
from ..Log import Log
from ..Record import Record


class Listcat():
    """Update fields in the CSV file regarding the VSAM datasets using the
    result of the command listcat executed in the mainframe.

    Attributes:
        _headers {list} -- List to store the headers from the program
            definition of the listcat CSV file.
        _file_path {string} -- Absolute path to the listcat CSV file.

    Methods:
        __init__() -- Initialize the class with its attributes.
        _read() -- Read the listcat CSV file and store the output in a
            dictionary.
        _analyze() -- Analyze data extracted from the listcat text file.
        _write() -- Write listcat records to the CSV file.
        _generate(file_path_txt) -- Convert listcat text file to a CSV file.
    """

    def __init__(self, file_path_txt):
        """Initializes the class with all the attributes.
        """
        self._headers = [column.name for column in LCol]
        self._file_path = Context().listcat_directory + '/listcat.csv'

        if file_path_txt:
            self._generate(file_path_txt)

        self._read()

    def _read(self):
        """Read the listcat CSV file and store the result in a dictionary.
        """
        Log().logger.debug(LogM.LISTCAT_READ.value % self._file_path)

        if FileHandler().check_path_exists(self._file_path):
            data = FileHandler().read_file(self._file_path)

            if data is not None:

                for i in range(1, len(data)):
                    row = data[i]
                    Context().listcat_records[row[0]] = row
        else:
            Log().logger.warning(LogM.LISTCAT_SKIP.value % self._file_path)

    def _analyze(self, data_list):
        """Analyze data extracted from the listcat text file.

        Returns:
            integer -- Return code of the method.
        """
        status = 0
        flag = 0
        lines = data_list.splitlines()
        data_dict = collections.OrderedDict()

        listcat_record = Record(LCol)
        record = listcat_record.columns

        for line in lines:

            if 'LISTING FROM CATALOG' in line:
                fields = line.split(' -- ')
                record[LCol.CATALOG.value] = fields[1].strip()

            if flag == 0 and 'DATA -------' in line:
                flag = 1

            if flag == 1 and 'CLUSTER--' in line:
                fields = line.split('--')
                if not fields[1].startswith('...'):
                    Log().logger.debug(LogM.DATASET_IDENTIFIED.value %
                                       fields[1])
                    flag = 2
                    record[LCol.DSN.value] = fields[1]
                    record[LCol.RECFM.value] = 'VB'

            elif flag == 2 and 'ATTRIBUTES' in line:
                flag = 3

            elif flag == 3 and 'STATISTICS' not in line:
                dataset_attributes = line.replace('-', '')
                dataset_attributes = dataset_attributes.split()

                for attr in dataset_attributes:
                    if attr.startswith('RKP'):
                        record[LCol.KEYOFF.value] = attr.replace('RKP', '')
                    elif attr.startswith('KEYLEN'):
                        record[LCol.KEYLEN.value] = attr.replace('KEYLEN', '')
                    elif attr.startswith('MAXLRECL'):
                        record[LCol.MAXLRECL.value] = attr.replace(
                            'MAXLRECL', '')
                    elif attr.startswith('AVGLRECL'):
                        record[LCol.AVGLRECL.value] = attr.replace(
                            'AVGLRECL', '')
                    elif attr.startswith('CISIZE'):
                        record[LCol.CISIZE.value] = attr.replace('CISIZE', '')
                    elif attr.startswith('INDEXED'):
                        record[LCol.VSAM.value] = 'KS'
                    elif attr.startswith('NONINDEXED'):
                        record[LCol.VSAM.value] = 'ES'
                    elif attr.startswith('NUMBERED'):
                        record[LCol.VSAM.value] = 'RR'

            # Re-initialization for the next dataset
            elif flag == 3 and 'STATISTICS' in line:
                data_dict[record[LCol.DSN.value]] = record
                record = ['' for _ in range(len(LCol))]
                flag = 0

        #TODO No way to fail this at the moment
        if status == 0:
            result = 'SUCCESS'
            color = Color.GREEN.value
        else:
            result = 'FAILED'
            color = Color.RED.value

        Log().logger.info(color + LogM.LISTCAT_GEN_STATUS.value % result)

        return data_dict

    def _write(self, data):
        """Write listcat records to the CSV file.

        Opens the CSV file, writes the headers in the first row and then writes
        the data from the records.

        Returns:
            integer -- Return code of the method.
        """
        Log().logger.debug(LogM.LISTCAT_WRITE.value % self._file_path)

        # Writing column headers to CSV file
        if FileHandler().check_path_exists(self._file_path) is False:
            status = FileHandler().write_file(self._file_path, [self._headers])

            if status != 0:
                return status

        # Writing records to CSV file
        content = data.values()
        status = FileHandler().write_file(self._file_path, content, 'a')

        return status

    def _generate(self, file_path_txt):
        """Convert listcat text file to a CSV file.

        One listcat text file can contains the info of one or multiple datasets.
        """
        Log().logger.debug(LogM.START_LISTCAT_GEN.value)

        data = FileHandler().read_file(file_path_txt)
        data = self._analyze(data)

        self._write(data)

        Log().logger.debug(LogM.END_LISTCAT_GEN.value)
