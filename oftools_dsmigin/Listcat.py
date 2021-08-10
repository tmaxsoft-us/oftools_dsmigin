#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module that contains all functions required for an update of the CSV file for VSAM datasets.

    Typical usage example:
      listcat = Listcat()
      listcat.run(records)"""

# Generic/Built-in modules
import os

# Third-party modules

# Owned modules
from .Context import Context
from .Log import Log
from .MigrationEnum import Col
from .Utils import Utils


class Listcat(object):
    """A class to update certain fields in the CSV file regarding the VSAM datasets using the result of the comman listcat executed in the mainframe.

        Attributes:
            _listcat_list: A list, the name of the text file(s) that contains the listcat output.
            _listcat_result: A string, the data extracted from the listcat output file.
            _csv_records: A 2D-list, the elements of the CSV file containing all the dataset data.
            _listcat_records: A 2D-list, the elements of the listcat result containing updates for VSAM datasets. 

        Methods:
            __init__(): Initialize all attributes.
            _read(): Read the content of the listcat output file and store the result in a string.
            _analyze(): Analyze the data extracted from the listcat output file.
            _update_csv_records(): Take the liscat extracted data to update the CSV records.
            run(records): Main method for listcat data retrieval."""

    def __init__(self, record):
        """Initialize all attributes.
            """
        self._file_path = Context().listcat_directory + '/' + record[
            Col.DSN.value]

        self._data = None
        self._record = record
        self._listcat_record = []

    def read(self):
        """Read the content of the listcat output file and store the result in a string.

            One listcat file can contains the info of one or multiple datasets.

            Args:
                listcat_file: A string, the absolute path of the file.

            Returns:
                A string, the data extracted from the listcat text file."""
        rc = 0
        try:
            with open(self._file_path, mode='r') as fd:
                self._data = fd.read()

            if self._data != None:
                Log().logger.debug(
                    '[listcat] Listcat file successfully imported')
                rc = 0
            else:
                rc = -1
        except FileNotFoundError:
            Log().logger.info(
                '[listcat] FileNotFoundError: No such file or directory:' +
                self._file_path)
            Log().logger.info('[listcat] Skipping listcat info retrieval')
            rc = 1

        return rc

    def analyze(self):
        """Analyze the data extracted from the listcat output file.

            Returns:
                A list, the listcat information correctly formatted and organized."""
        rc = 0

        if self._data != None:
            lines = self._data.splitlines()

            # for i in range(len(lines)):
            #     fields = lines[i].split()
            #     # TODO update listcat result processing here
            #     if fields[0] == 'DSN':
            #         # recfm = lines[i + 1].split()[1]

            #         self._record[Col.VSAM.value] = ''
            #         self._record[Col.KEYOFF.value] = lines[i + 2].split()[2]
            #         self._record[Col.KEYLEN.value] = ''
            #         self._record[Col.MAXLRECL.value] = ''
            #         self._record[Col.AVGLRECL.value] = ''
            #         self._record[Col.CISIZE.value] = ''
            #         if self._record[Col.CISIZE.value] == 'INDEXED':
            #             self._record[Col.VSAM.value] = 'KS'

            flag = 0
            for line in lines:
                if flag == 1:                         
                    info = line.strip()
                    info = info.replace("-","")
                    infoList = info.split(' ')
                    print(info)
                    for j in range(len(infoList)):
                        if infoList[j].startswith("RKP"):
                            rkp = infoList[j].replace("RKP","")
                            self._record[Col.KEYOFF.value] = rkp
                            print("KEYOFF: " + str(rkp))
                        elif infoList[j].startswith("KEYLEN"):
                            keylen = infoList[j].replace("KEYLEN","")
                            self._record[Col.KEYLEN.value] = keylen
                            print("KEYLEN: " + str(keylen))
                        elif infoList[j].startswith("MAXLRECL"):
                            maxlrecl = infoList[j].replace("MAXLRECL","")
                            self._record[Col.MAXLRECL.value] = maxlrecl
                            print("MAXLRECL: " + str(maxlrecl))
                        elif infoList[j].startswith("AVGLRECL"):
                            avglrecl = infoList[j].replace("AVGLRECL","")
                            self._record[Col.AVGLRECL.value] = avglrecl
                            print("AVGLRECL: " + str(avglrecl))
                        elif infoList[j].startswith("CISIZE"):
                            cisize = infoList[j].replace("CISIZE","")
                            self._record[Col.CISIZE.value] = cisize
                            print("CISIZE: " + str(cisize))
                        elif infoList[j].startswith("INDEXED"):
                            vsam = "KS"
                            self._record[Col.VSAM.value] = vsam
                            print("VSAM: " + vsam)
                if line.find("DATA ------- " + self._record[Col.DSN.value]) >= 0:
                    flag = 1
                    self._record[Col.RECFM.value] = "VB"
                if line.find("INDEX ------ " + self._record[Col.DSN.value]) >= 0:            
                    break

        return rc

    def update_dataset_record(self):
        """Take the liscat extracted data to update the CSV records.

            It first update the CSV records with different data regarding the VSAM datasets, data required for a successful migration of this type of dataset. Then, it also look for each VSAM datasets if there are the equivalent 'INDEX and 'DATA'. These datasets are not useful for migration, so the tool removes them.

            Returns:
                A 2D-list, the updated dataset data with listcat information for VSAM datasets."""
        rc = 0

        if self._data != None:
            dsn_list = []
            records = Context().records
            for record in records:
                dsn_list.append(record.columns[Col.DSN.value])
            # dsn_list = [records.columns[Col.DSN.value] for _ in records]

            index_dsn = self._record[Col.DSN.value] + '.INDEX'
            if index_dsn in dsn_list:
                # Replace the value in the column named DSORG by VSAM in the records list
                self._record[Col.DSORG.value] = 'VSAM'
                # Identify the position of the index DSN in the dsn_list
                i = dsn_list.index(index_dsn)
                # Remove the line where this DSN appears in the records list
                Context().records.remove(Context().records[i])
                Log().logger.info(
                    'Removed from dataset list: ' + index_dsn +
                    '. This is not useful for migration to OpenFrame.')

            data_dsn = self._record[Col.DSN.value] + '.DATA'
            if data_dsn in dsn_list:
                self._record[Col.DSORG.value] = 'VSAM'
                # Identify the position of the data DSN in the dsn_list
                j = dsn_list.index(data_dsn)
                # Remove the line where this DSN appears in the records list
                Context().records.remove(Context().records[j])
                Log().logger.info(
                    '[LISTCAT] Removed from dataset list: ' + data_dsn +
                    '. This is not useful for migration to OpenFrame.')

        return rc
