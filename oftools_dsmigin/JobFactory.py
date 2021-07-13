#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module retrieves the parameters entered by the user and launches the corresponding job.

Typical usage example:

  job_factory = JobFactory()
  job_factory.create('update')
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .DownloadJob import DownloadJob
from .ListcatJob import ListcatJob
from .MigrationJob import MigrationJob
from .UpdateJob import UpdateJob


class JobFactory(object):
    """Class following the Factory pattern to execute different jobs depending on the user input.

    Methods:
        create(input): Create the job according to the input parameter.
    """

    def create(self, input):
        """Create the job according to the input parameter.

        Args:
            input: Input parameter to launch the appropriate Job.

        Returns:
            A Job object, the appropriate job.
        """
        if input == 'update':
            return UpdateJob()
        elif input == 'listcat':
            return ListcatJob()
        elif input == 'download':
            return DownloadJob()
        elif input == 'migration':
            return MigrationJob()

        assert True == 'undefined Job found'
        return None