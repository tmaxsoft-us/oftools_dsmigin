#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module that contains all functions required for an update of the CSV file for VSAM datasets.

Typical usage example:
    listcat = Listcat()
    listcat.run(records)
"""

# Generic/Built-in modules
import collections

# Third-party modules

# Owned modules
from .Context import Context
from .enums.MessageEnum import Color, LogM
from .enums.MigrationEnum import Col
from .enums.ListcatEnum import LCol
from .handlers.FileHandler import FileHandler
from .Log import Log


class Listcat(object):
    """A class to update certain fields in the CSV file regarding the VSAM datasets using the result of the command listcat executed in the mainframe.

    Attributes:
        _headers {list} -- List to store the headers from the program definition on the listcat CSV file.
        _file_path {string} -- Absolute path to the listcat file, either TXT or CSV.
        _data_txt {} -- List with the data extracted from the listcat text file.
        _data {} -- Dictionary with the listcat datasets info.

    Methods:
        __init__() -- Initializes all attributes of the class.
        _read_txt() -- Reads the listcat text file and store the output in a list.
        _get_data_txt() -- Analyzes the data extracted from the listcat text file.
        _write_csv() -- Writes the dataset listcat records changes to the CSV file.
        generate_csv() -- Main method to convert the listcat TXT file to a CSV file.
        read_csv() -- Reads the content of the listcat CSV file and store the result in a list.
    """

    def __init__(self, file_path):
        """Initializes the class with all the attributes.
        """
        self._name = 'listcat'
        self._headers = [column.name for column in LCol]

        self._file_path_csv = Context().listcat_directory + '/listcat.csv'
        self._file_path_txt = file_path

        self._data_csv = collections.OrderedDict()
        self._data_txt = []

    @property
    def data(self):
        """Getter method for the attribute _data.
        """
        return self._data_csv

    def _read(self, extension=''):
        """Reads the listcat file and store the output.

        This can read a listcat text file and store the output in a list, or read a listcat CSV file and store the output in a dictionary

        Arguments:
            extension {string} --
        """
        if extension == 'txt':
            data = FileHandler().read_file(self._file_path_txt)
            self._data_txt = data.splitlines()

        elif extension == 'csv':
            data = FileHandler().read_file(self._file_path_csv)
            for i in range(1, len(data)):
                row = data[i]
                self._data_csv[row[0]] = row[1:]
        else:
            print('error')

    def _analyze_txt(self):
        """Analyzes the data extracted from the listcat text file.

        Returns:
            integer -- Return code of the method.
        """
        rc = 0
        flag = 0

        for line in self._data_txt:

            if 'LISTING FROM CATALOG' in line:
                fields = line.split(' -- ')
                catalog = fields[1].strip()

            if flag == 0 and 'DATA -------' in line:
                flag = 1

            if flag == 1 and 'CLUSTER--' in line:
                fields = line.split('--')
                if not fields[1].startswith('...'):
                    Log().logger.debug(LogM.DATASET_IDENTIFIED.value %
                                       (self.name, fields[1]))
                    flag = 2
                    dsn = fields[1]
                    recfm = 'VB'
                    vsam = ''
                    keyoff, keylen = '', ''
                    maxlrecl, avglrecl = '', ''
                    cisize = ''

            elif flag == 2 and 'ATTRIBUTES' in line:
                # Log().logger.debug('Attributes section found')
                flag = 3

            elif flag == 3 and 'STATISTICS' not in line:
                # Log().logger.debug('Analyzing attributes')
                dataset_attributes = line.replace('-', '')
                dataset_attributes = dataset_attributes.split()

                for attr in dataset_attributes:
                    if attr.startswith('RKP'):
                        keyoff = attr.replace('RKP', '')
                    elif attr.startswith('KEYLEN'):
                        keylen = attr.replace('KEYLEN', '')
                    elif attr.startswith('MAXLRECL'):
                        maxlrecl = attr.replace('MAXLRECL', '')
                    elif attr.startswith('AVGLRECL'):
                        avglrecl = attr.replace('AVGLRECL', '')
                    elif attr.startswith('CISIZE'):
                        cisize = attr.replace('CISIZE', '')
                    elif attr.startswith('INDEXED'):
                        vsam = 'KS'
                    elif attr.startswith('NONINDEXED'):
                        vsam = 'ES'
                    elif attr.startswith('NUMBERED'):
                        vsam = 'RR'

            # Re-initialization for the next dataset
            elif flag == 3 and 'STATISTICS' in line:
                self._data[dsn] = [
                    recfm, vsam, keyoff, keylen, maxlrecl, avglrecl, cisize,
                    catalog
                ]
                flag = 0

        if rc == 0:
            status = 'SUCCESS'
            color = Color.GREEN.value
        #TODO No way to fail this at the moment
        else:
            status = 'FAILED'
            color = Color.RED.value

        Log().logger.info(color + LogM.LISTCAT_CSV_FILE_STATUS.value % status)

        return rc

    def _write_csv(self):
        """Writes the dataset listcat records changes to the CSV file.
        
        Opens the CSV file, writes the headers in the first row and then writes the data from the records.

        Returns:
            integer -- Return code of the method.
        """
        # Writing column headers to CSV file
        if FileHandler().check_path_exists(self._file_path_csv) is False:
            rc = FileHandler().write_file(self._file_path_csv, self._headers)

        if rc != 0:
            return rc

        # Writing records to CSV file
        for key, value in self._data_csv.items():
            record = [key] + value
            rc = FileHandler().write_file(self._file_path_csv, record, 'a')
            if rc != 0:
                break

        return rc

    def generate_csv(self):
        """Main method to convert the listcat TXT file to a CSV file.
        """
        Log().logger.debug(LogM.START_LISTCAT_GEN.value % self._name)

        self._read('txt')
        self._analyze_txt()
        self._write_csv()

        Log().logger.debug(LogM.END_LISTCAT_GEN.value % self._name)

    def read_csv(self):
        """Reads the content of the listcat CSV file and store the result in a list.

        One listcat file can contains the info of one or multiple datasets.
        """

        data_csv = FileHandler().read_file(self._file_path_csv)

        for i in range(1, len(data_csv)):
            row = data_csv[i]
            self._data_csv[row[0]] = row[1:]

    def update_index_and_data(self, record):
        """Take the listcat extracted data to update the CSV records.

        It first updates the CSV records with different data regarding the VSAM datasets, data required for a successful migration of this type of dataset. Then, it also look for each VSAM datasets if there are the equivalent 'INDEX and 'DATA'. These datasets are not useful for migration, so the tool removes them.

        Arguments:
            record {list} -- The given listcat record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
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
                Log().logger.info(LogM.REMOVE_DATASET.value %
                                  (self._name, index_dsn))

            data_dsn = record[Col.DSN.value] + '.DATA'
            if data_dsn in dsn_list:
                record[Col.DSORG.value] = 'VSAM'
                # Identify the position of the data DSN in the dsn_list
                j = dsn_list.index(data_dsn)
                # Remove the line where this DSN appears in the records list
                Context().records.remove(Context().records[j])
                Log().logger.info(LogM.REMOVE_DATASET.value %
                                  (self._name, data_dsn))

        return rc
