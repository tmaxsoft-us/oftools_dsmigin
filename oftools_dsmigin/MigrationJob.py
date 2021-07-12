#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""This modules runs the Migration Job.

Typical usage example:

  job = MigrationJob()
  job.run()
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .CSV import CSV
from .DSMIGINHandler import DSMIGINHandler
from .Job import Job
from .Statistics import Statistics


class MigrationJob(Job):
    """A class used to run the migration job.

    This class contains a run method that executes all the steps of the job.

    Methods:
        run(): Perform all the steps to migrate datasets in OpenFrame using dsmigin and update the CSV file.
    """

    def run(self):
        """Perform all the steps to migrate datasets in OpenFrame using dsmigin and update the CSV file.

        It first creates a backup of the CSV file and loads it. Then, it executes the dsmigin command to migrate datasets and updating the DSMIGIN status (success or fail) at the same time. It finally writes the changes to the CSV, and updates the statistics.

        Returns:
            An integer, the return code of the job.
        """
        rc = 0

        csv_file = CSV()
        csv_file.backup()
        records = csv_file.read()

        dsmigin = DSMIGINHandler()
        records = dsmigin.run(records)

        rc = csv_file.write(records)

        statistics = Statistics()
        rc = statistics.run(records)

        return rc