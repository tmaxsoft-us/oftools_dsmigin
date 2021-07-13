#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module that contains all functions required for an update of the CSV file for VSAM datasets.

Typical usage example:

  listcat = Listcat()
  listcat.run(records)
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .Context import Context
from .MigrationEnum import Col


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
        run(records): Main method for listcat data retrieval.
    """

    def __init__(self):
        """Initialize all attributes.
        """
        self._listcat_list = Context().get_listcat_result()
        self._listcat_result = ''
        self._csv_records = []
        self._listcat_records = []

    def _read(self, listcat_file):
        """Read the content of the listcat output file and store the result in a string.

        One listcat file can contains the info of one or multiple datasets.

        Args:
            listcat_file: A string, the absolute path of the file.

        Returns:
            A string, the data extracted from the listcat text file.
        """
        with open(listcat_file, 'r') as file_data:
            self._listcat_result = file_data.read()

        return self._listcat_result

    def _analyze(self):
        """Analyze the data extracted from the listcat output file.

        Returns:
            A list, the listcat information correctly formatted and organized.
        """
        lines = self._listcat_result.splitlines()

        for i in range(len(lines)):
            fields = lines[i].split()
            # TODO Add listcat result processing here
            if fields[0] == 'DSN':
                record = []
                recfm = lines[i+1].split()[1]
                keyoff = lines[i+2].split()[2]
                record.append(recfm, keyoff)

                self._listcat_records.append(record)
            
        return self._listcat_records

    def _update_csv_records(self):
        """Take the liscat extracted data to update the CSV records.

        It first update the CSV records with different data regarding the VSAM datasets, data required for a successful migration of this type of dataset. Then, it also look for each VSAM datasets if there are the equivalent 'INDEX and 'DATA'. These datasets are not useful for migration, so the tool removes them.

        Returns:
            A 2D-list, the updated dataset data with listcat information for VSAM datasets.
        """
        csv_dsn_list = [csv_record[Col.DSN.value] for csv_record in self._csv_records]
        listcat_dsn_list = [listcat_record[Col.DSN.value] for listcat_record in self._listcat_records]

        for i in range(len(self._csv_records)):
            csv_record = self._csv_records[i]
            dsn = csv_record[Col.DSN.value]
            index = dsn + '.INDEX'
            data = dsn + '.DATA'
            
            # If record needs to be updated
            if dsn in listcat_dsn_list:
                # Find the updates in the listcat records
                j = listcat_dsn_list.index(dsn)
                listcat_record = self._listcat_records[j]

                # Updating the fields in the records list
                csv_record[i][Col.RECFM.value] = listcat_record[Col.RECFM.value]
                csv_record[i][Col.KEYOFF.value] = listcat_record[Col.KEYOFF.value]
                csv_record[i][Col.KEYLEN.value] = listcat_record[Col.KEYLEN.value]
                csv_record[i][Col.MAXLRECL.value] = listcat_record[Col.MAXLRECL.value]
                csv_record[i][Col.AVGLRECL.value] = listcat_record[Col.AVGLRECL.value]
                csv_record[i][Col.CISIZE.value] = listcat_record[Col.CISIZE.value]
                if listcat_record[Col.CISIZE.value] == 'INDEXED':
                    csv_record[i][Col.VSAM.value] = 'KS'
                # TODO Finish the update of the fields
            
            if index in csv_dsn_list:
                # Replace the value in the column named DSORG by VSAM in the records list
                csv_record[i][Col.DSORG.value] = 'VSAM'
                # Identify the position of the index DSN in the dsn_list
                k = csv_dsn_list.index(index)
                # Remove the line where this DSN appears in the records list
                self._csv_records.remove(self._csv_records[k])
                print('Removed from dataset list: ' + index + '. This is not useful for migration to OpenFrame.')
            
            if data in csv_dsn_list:
                # Replace the value in the column named DSORG by VSAM in the records list
                csv_record[i][Col.DSORG.value] = 'VSAM'
                # Identify the position of the data DSN in the dsn_list
                k = csv_dsn_list.index(data)
                # Remove the line where this DSN appears in the records list
                self._csv_records.remove(self._csv_records[k])
                print('Removed from dataset list: ' + data + '. This is not useful for migration to OpenFrame.')
            
        return self._csv_records

    def run(self, records):
        """Main method for listcat data retrieval.

        Args:
            records: A 2D-list, dataset data before the update form the listcat information.

        Returns:
            A 2D-list, dataset data after all the changes applied in the Listcat module.
        """
        self._csv_records = records

        for listcat_file in self._listcat_list:
            self._read(listcat_file)
            self._analyze()

        self._update_csv_records()

        return self._csv_records
