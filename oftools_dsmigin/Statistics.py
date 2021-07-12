#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Compute statistics on the CSV file to provide a better understanding on the progress of the different tasks to the user.

Typical usage example:

  statistics = Statistics()
  statistics.run(records)
"""

# Generic/Built-in modules
import csv
import datetime
import os

# Third-party modules

# Owned modules
from .Context import Context
from .MigrationEnum import Col


class Statistics():
    """A class used to compute statistics on the CSV file regarding the success/failure of the download/migration execution.

    Attributes:
        _work_directory: A string, working directory for the program execution.
        _csv_root_file_name: A string, the name of the CSV file without extension.
        _tag: A string, the tag option used by the user.
        _timestamp: A string, the date and time of execution of the program in a certain format.
        _headers: A list, headers of the columns for the different statistics.
        _statistics: A list, the values of the statistics regarding the CSV file.
        _records: A 2D-list, the elements of the CSV file containing all the dataset data.

    Methods:
        __init__(): Initializes all attributes.
        _analyze_download(record): Retrieve the count of success/failure of the download execution.
        _analyze_download(record): Retrieve the count of success/failure of the migration execution.
        _analyze(): Analyze the CSV file and compute statistics. Store all the statistics in a list.
        _statistics_to_file(): Create a new CSV file to write and save the statistics.
        _print(): Print to the user the CSV statistics in a nice visualization.
        run(records): Main run method for the statistics computation.
    """

    def __init__(self):
        """Initializes all attributes.
        """
        self._work_directory = Context().get_work_directory()

        csv_file_path = Context().get_input_csv()
        csv_file_name = csv_file_path.rsplit('/')[0]
        self._csv_root_file_name = csv_file_name.split('.')[0]
        self._tag = Context().get_tag()

        today = datetime.datetime.today()
        self._timestamp = today.strftime('%Y%m%d_%H%M%S')

        self._headers = []
        self._statistics = []
        self._records = []

    def _analyze_download(self, record):
        """Retrieve the count of success/failure of the download execution.
        """
        unset_list = ('', ' ', None)

        # Download count
        if record[Col.FTP.value] == 'S':
            self._statistics[0] += 1
        elif record[Col.FTP.value] == 'F':
            self._statistics[2] += 1

        if record[Col.FTPDURATION.value] not in unset_list:
            self._statistics[4] += float(record[Col.FTPDURATION.value])

    def _analyze_migration(self, record):
        """Retrieve the count of success/failure of the migration execution.
        """
        unset_list = ('', ' ', None)

        # Migration count
        if record[Col.DSMIGIN.value] == 'S':
            self._statistics[6] += 1
        elif record[Col.DSMIGIN.value] == 'F':
            self._statistics[8] += 1

        if record[Col.DSMIGINDURATION.value] not in unset_list:
            self._statistics[10] += float(record[Col.DSMIGINDURATION.value])

    def _analyze(self):
        """Analyze the CSV file and compute statistics. Store all the statistics in a list.

        It currently supports: 
            - Successful downloads, Success download rate
            - Failed downloads, Fail download rate
            - Total download time, Average download time
            - Successful migrations, Success migration rate
            - Failed migrations, Fail migration rate
            - Total migration time, Average migration time
            - Number of lines, so the number of datasets

        # TODO Same metrics but categorized per DSORG, create an enumeration to handle all the different columns
        """
        rc = 0

        self._headers.extend([
            'DOWNNLOAD_SUCCESS_COUNT', 'DOWNLOAD_SUCCESS_PERCENTAGE',
            'DOWNLOAD_FAIL_COUNT', 'DOWNLOAD_FAIL_PERCENTAGE',
            'DOWNLOAD_TOTAL_TIME', 'DOWNLOAD_AVERAGE_TIME'
        ])
        self._statistics.extend([0, 0, 0, 0, 0.0, 0.0])

        self._headers.extend([
            'MIGRATION_SUCCESS_COUNT', 'MIGRATION_SUCCESS_PERCENTAGE',
            'MIGRATION_FAIL_COUNT', 'MIGRATION_FAIL_PERCENTAGE',
            'MIGRATION_TOTAL_TIME', 'MIGRATION_AVERAGE_TIME'
        ])
        self._statistics.extend([0, 0, 0, 0, 0.0, 0.0])

        # Count the number of dataset
        self._headers.append('NUMBER_OF_DATASETS')
        number_of_records = len(self._records)
        self._statistics.append(number_of_records)

        for record in self._records:
            self._analyze_download(record)
            self._analyze_migration(record)

        self._statistics[1] = (self._statistics[0] / number_of_records) * 100
        self._statistics[3] = (self._statistics[2] / number_of_records) * 100
        self._statistics[5] = (self._statistics[4] / number_of_records) * 100

        self._statistics[7] = (self._statistics[6] / number_of_records) * 100
        self._statistics[9] = (self._statistics[8] / number_of_records) * 100
        self._statistics[11] = (self._statistics[10] / number_of_records) * 100

        return rc

    def _statistics_to_file(self):
        """Create a new CSV file to write and save the statistics.

        Returns:
            An integer, the return code of the method.
        """
        rc = 0
        statistics_directory = self._work_directory + '/csv_statistics'
        statistics_file_name = self._csv_root_file_name + '_' + self._tag + '_' + self._timestamp + '_statistics.csv'

        try:
            # Creating the statistics folder if it does not exist already
            if not os.path.exists(statistics_directory):
                os.mkdirs(statistics_directory)
        except:
            print(
                'CSV statistics directory creation failed. Permission denied.')

        statistics_file_path = statistics_directory + statistics_file_name
        try:
            # Creating the CSV statistics file
            with open(statistics_file_path, 'w') as statistics:
                statistics_data = csv.writer(statistics, delimiter=',')
                # Writing column headers to CSV statistics file
                statistics_data.writerow(self._headers)
                # Writing statistics
                statistics_data.writerow(self._statistics)
        except:
            print('CSV statistics file creation failed. Permission denied.')

        return rc

    def _print(self):
        """Print to the user the CSV statistics in a nice visualization.
        """
        #TODO Work on paper on a nice table to visualize these statistics
        print('Number of datasets\n==================\n')
        print('PO\t\tPS\t\tVSAM\t\t\t\tTotal')

    def run(self, records):
        """Main run method for the statistics computation.

        Args:
            records: A 2D-list, the elements of the CSV file containing all the dataset data.

        Returns:
            An integer, the return code of the method.
        """
        rc = 0
        self._records = records

        rc = self._analyze()
        rc = self._statistics_to_file()
        self._print()

        return rc
