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
from ..Context import Context
from ..enums.MessageEnum import Color, LogM
from ..enums.ListcatEnum import LCol
from ..handlers.FileHandler import FileHandler
from ..Log import Log


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

    def __init__(self, txt_file_path):
        """Initializes the class with all the attributes.
        """
        self._headers = [column.name for column in LCol]
        self._file_path = Context().listcat_directory + '/listcat.csv'

        if txt_file_path:
            self._generate(txt_file_path)

        self._read()

    def _read(self):
        """Reads the content of the listcat CSV file and store the result in a list.

        One listcat file can contains the info of one or multiple datasets.
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
        """Analyzes the data extracted from the listcat text file.

        Returns:
            integer -- Return code of the method.
        """
        rc = 0
        flag = 0
        lines = data_list.splitlines()
        data_dict = collections.OrderedDict()

        for line in lines:

            if 'LISTING FROM CATALOG' in line:
                fields = line.split(' -- ')
                catalog = fields[1].strip()

            if flag == 0 and 'DATA -------' in line:
                flag = 1

            if flag == 1 and 'CLUSTER--' in line:
                fields = line.split('--')
                if not fields[1].startswith('...'):
                    Log().logger.debug(LogM.DATASET_IDENTIFIED.value %
                                       fields[1])
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
                data_dict[dsn] = [
                    dsn, recfm, vsam, keyoff, keylen, maxlrecl, avglrecl,
                    cisize, catalog
                ]
                flag = 0

        #TODO No way to fail this at the moment
        if rc == 0:
            status = 'SUCCESS'
            color = Color.GREEN.value
        else:
            status = 'FAILED'
            color = Color.RED.value

        Log().logger.info(color + LogM.LISTCAT_GEN_STATUS.value % status)

        return data_dict

    def _write(self, data):
        """Writes the dataset listcat records changes to the CSV file.

        Opens the CSV file, writes the headers in the first row and then writes the data from the records.

        Returns:
            integer -- Return code of the method.
        """
        Log().logger.debug(LogM.LISTCAT_WRITE.value % self._file_path)

        # Writing column headers to CSV file
        if FileHandler().check_path_exists(self._file_path) is False:
            rc = FileHandler().write_file(self._file_path, [self._headers])

            if rc != 0:
                return rc

        # Writing records to CSV file
        content = data.values()
        rc = FileHandler().write_file(self._file_path, content, 'a')

        return rc

    def _generate(self, file_path_txt):
        """Main method to convert the listcat TXT file to a CSV file.
        """
        Log().logger.debug(LogM.START_LISTCAT_GEN.value)

        data = FileHandler().read_file(file_path_txt)
        data = self._analyze(data)

        self._write(data)

        Log().logger.debug(LogM.END_LISTCAT_GEN.value)
