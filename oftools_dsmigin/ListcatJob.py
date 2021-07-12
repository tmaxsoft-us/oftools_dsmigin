#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""This modules runs the Listcat Job.

Typical usage example:

  job = ListcatJob()
  job.run()
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .CSV import CSV
from .Job import Job
from .Listcat import Listcat
from .Statistics import Statistics


class ListcatJob(Job):
    """A class used to run the listcat job.

    This class contains a run method that executes all the steps of the job.

    Methods:
        run(): Perform all the steps to exploit the listcat file and update the CSV file.

    """

    def run(self):
        """Perform all the steps to exploit the listcat file and update the CSV file.

        It first creates a backup of the CSV file and loads it. Then it analyzes and exploits the listcat result file. Finally, it writes the changes to the CSV file and updates the statistics.

        Returns:  
            An integer, the return code of the job. 
        """
        rc = 0
        records = []

        csv_file = CSV()
        rc = csv_file.backup()
        records = csv_file.read()

        listcat = Listcat()
        records = listcat.run(records)

        rc = csv_file.write(records)
        statistics = Statistics()
        rc = statistics.run(records)

        return rc