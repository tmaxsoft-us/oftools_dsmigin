#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module that contains all functions required for an update of the CSV file for VSAM datasets.

    Typical usage example:
        listcat = Listcat()
        listcat.run(records)
    """

# Generic/Built-in modules
import collections
import csv

# Third-party modules

# Owned modules
from .Context import Context
from .Log import Log
from .MigrationEnum import Col
from .ListcatEnum import LCol
from .Utils import Utils


class Listcat(object):
    """A class to update certain fields in the CSV file regarding the VSAM datasets using the result of the comman listcat executed in the mainframe.

        Attributes:
            _headers {list} -- List to store the headers from the program definition on the listcat CSV file.
            _file_path {string} -- Absolute path to the listcat file, either TXT or CSV.
            _data_txt {} -- List with the data extracted from the listcat text file.
            _data {} -- Dictionary with the liscat datasets info.

        Methods:
            __init__() -- Initializes all attributes of the class.
            _read_txt() -- Reads the listcat text file and store the output in a list.
            _get_data_txt() -- Analyzes the data extracted from the listcat text file.
            _write_csv() -- Writes the dataset listcat records changes to the CSV file.
            generate_csv() -- Main method to convert the listcat TXT file to a CSV file.
            read_csv() -- Reads the content of the listcat CSV file and store the result in a list.
        """

    def __init__(self, file_path):
        """Initializes all attributes of the class.
            """
        self._headers = [column.name for column in LCol]

        self._file_path = file_path

        self._data_txt = []
        self._data = collections.OrderedDict()

    @property
    def data(self):
        """Getter method for the attribute _data.
            """
        return self._data

    def _read_txt(self):
        """Reads the listcat text file and store the output in a list.
            """
        file_data = Utils().read_file(self._file_path)
        self._data_txt = file_data.splitlines()

    def _get_data_txt(self):
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

            if flag == 0 and 'CLUSTER--' in line:
                fields = line.split('--')
                if not fields[1].startswith('...'):
                    Log().logger.debug('Dataset identified:' + fields[1])
                    flag = 1
                    dsn = fields[1]
                    recfm = 'VB'
                    vsam = ''
                    keyoff, keylen = '', ''
                    maxlrecl, avglrecl = '', ''
                    cisize = ''

            elif flag == 1 and 'ATTRIBUTES' in line:
                # Log().logger.debug('Attributes section found')
                flag = 2

            elif flag == 2 and 'STATISTICS' not in line:
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
            elif flag == 2 and 'STATISTICS' in line:
                self._data[dsn] = [
                    recfm, vsam, keyoff, keylen, maxlrecl, avglrecl, cisize,
                    catalog
                ]
                flag = 0

        if rc == 0:
            status = 'SUCCESS'
            Log().logger.info('[listcat] CSV successfully generated: ' +
                              self._file_path)
        #TODO No way to fail this at the moment
        else:
            status = 'FAILED'

        Log().logger.info('LISTCAT FILE ' + status)

        return rc

    def _write_csv(self):
        """Writes the dataset listcat records changes to the CSV file.
        
            Opens the CSV file, writes the headers in the first row and then writes the data from the records.

            Returns:
                integer -- Return code of the method.
                
            Raises:
                OSError -- Exception is raised if there is an issue finding or opening the file.
            """
        try:
            with open(Context().listcat_directory + '/listcat.csv', 'a') as fd:
                writer = csv.writer(fd, delimiter=',')
                # Writing column headers to CSV file
                writer.writerow(self._headers)

                # Writing records to CSV file
                for key, value in self._data.items():
                    record = [key] + value
                    writer.writerow(record)
            rc = 0
        except OSError as e:
            Log().logger.error('OSError: ' + str(e))
            rc = -1

        return rc

    def generate_csv(self):
        """Main method to convert the listcat TXT file to a CSV file.
            """
        Log().logger.debug('[listcat] Starting Listcat CSV generation')
        self._read_txt()
        self._get_data_txt()
        #TODO with the refactoring implement something to read the CSV first. Append and update if already exist, create and write if not
        self._write_csv()

        Log().logger.debug('[listcat] Ending Listcat CSV generation')

    def read_csv(self):
        """Reads the content of the listcat CSV file and store the result in a list.

            One listcat file can contains the info of one or multiple datasets.

            Arguments:
                listcat_file: A string, the absolute path of the file.

            Returns:
                A string, the data extracted from the listcat text file.
            """
        rc = 0
        i = 0

        try:
            with open(self._file_path, mode='r') as fd:
                reader = csv.reader(fd, delimiter=',')
                for row in reader:
                    # if i == 0:
                    #     rc = self._check_headers(reader[i])
                    # else:
                    if i > 0:
                        self._data[row[0]] = row[1:]

                    i += 1
            rc = 0

            # if self._data != None:
            #     Log().logger.debug('[listcat] Listcat file import successful')
            #     rc = 0
            # else:
            #     Log().logger.error('[listcat] Listcat file import failed')
            #     rc = -1

        except FileNotFoundError:
            Log().logger.warning(
                '[listcat] FileNotFoundError: No such file or directory:' +
                self._file_path)
            rc = 1

        finally:
            return rc

    def update_index_and_data(self, record):
        """Take the liscat extracted data to update the CSV records.

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
                Log().logger.info(
                    'Removed from dataset list: ' + index_dsn +
                    '. This is not useful for migration to OpenFrame.')

            data_dsn = record[Col.DSN.value] + '.DATA'
            if data_dsn in dsn_list:
                record[Col.DSORG.value] = 'VSAM'
                # Identify the position of the data DSN in the dsn_list
                j = dsn_list.index(data_dsn)
                # Remove the line where this DSN appears in the records list
                Context().records.remove(Context().records[j])
                Log().logger.info(
                    '[LISTCAT] Removed from dataset list: ' + data_dsn +
                    '. This is not useful for migration to OpenFrame.')

        return rc
