#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create jobs.

Typical usage example:
  job_factory = JobFactory()
  job_factory.create('ftp')
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .FTPJob import FTPJob
from .ListcatJob import ListcatJob
from .MigrationJob import MigrationJob


class JobFactory():
    """Create jobs.

    This class is the core of the Factory design pattern.

    Methods:
        create(job_name) -- Create the job according to the input parameter.
    """

    def create(self, job_name):
        """Create the job according to the input parameter.

        Arguments:
            job_name {string} -- Name of the job.

        Returns:
            Job object.
        """
        if job_name == 'ftp':
            return FTPJob(job_name)
        if job_name == 'listcat':
            return ListcatJob(job_name)
        if job_name == 'migration':
            return MigrationJob(job_name)

        return None
