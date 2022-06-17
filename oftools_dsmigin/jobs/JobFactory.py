#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module retrieves the parameters entered by the user and creates the corresponding job.

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


class JobFactory(object):
    """A class used to create all the jobs required with the given input parameters. 
    
    This class is the core of the Factory design pattern.

    Methods:
        create(job_name) -- Creates the job according to the input parameter.
    """

    def create(self, job_name):
        """Creates the job according to the input parameter.

        Arguments:
            job_name {string} -- Name of the job.

        Returns:
            Job object -- Appropriate Job object depending on the input.
        """
        if job_name == 'ftp':
            return FTPJob(job_name)
        elif job_name == 'listcat':
            return ListcatJob(job_name)
        elif job_name == 'migration':
            return MigrationJob(job_name)
        else:
            return None