#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""This modules runs the Update Job.

Typical usage example:

  job = UpdateJob()
  job.run()
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .CSV import CSV
from .FTPHandler import FTPHandler
from .Job import Job
from .Statistics import Statistics


class UpdateJob(Job):
    """A class used to run the update job.

    This class contains a run method that executes all the steps of the job.

    Methods:
        run(): Perform all the steps to update the CSV file.
    """

    def run(self):
        """Perform all the steps to update the CSV file.

        It first create a backup of the first CSV file that contains dataset names only and reads it. Then it executes an FTP command to retrieve datasets info from the mainframe, and finally writes the changes to the CSV file. It also creates statistics regarding the CSV file.

        Returns: 
            An integer, the return code of the job.
        """
        rc = 0
        records = []

        csv_file = CSV()
        rc = csv_file.backup()
        records = csv_file.read()

        ftp = FTPHandler()
        records = ftp.get_mainframe_dataset_info(records)

        rc = csv_file.write(records)

        statistics = Statistics()
        rc = statistics.run(records)

        return rc