#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""This modules runs the Download Job.

Typical usage example:

  job = DownloadJob()
  job.run()
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .CSV import CSV
from .FTPHandler import FTPHandler
from .Job import Job
from .Statistics import Statistics


class DownloadJob(Job):
    """A class used to run the download job.

    This class contains a run method that executes all the steps of the job.

    Methods:
        run(): Perform all the steps to download datasets using FTP and update the CSV file.
    """

    def run(self):
        """Perform all the steps to download datasets using FTP and update the CSV file.

        It first creates a backup of the CSV file and loads it. Then, it executes the FTP command to download datasets and updating the FTP status (success or fail) at the same time. It finally writes the changes to the CSV, and updates the statistics.

        Returns: 
            An integer, the return code of the job.
        """
        rc = 0
        records = []

        csv_file = CSV()
        csv_file.backup()
        records = csv_file.read()

        ftp = FTPHandler()
        records = ftp.download(records)

        csv_file.write(records)

        statistics = Statistics()
        rc = statistics.run(records)

        return rc