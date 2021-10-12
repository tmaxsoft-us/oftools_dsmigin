#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module retrieves the parameters entered by the user and creates the corresponding job.

    Typical usage example:
        job_factory = JobFactory()
        job_factory.create('update')
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

        Attributes:
            _storage_resource {Storage Resource object} -- Object where the program read and write the data. It could be a CSV file or a database table.

        Methods:
            __init__(storage_resource) -- Initializes the only attribute of the class.
            create(input) -- Creates the job according to the input parameter.
        """

    def __init__(self, storage_resource):
        """Initializes the only attribute of the class.
            """
        self._storage_resource = storage_resource

    def create(self, job_name):
        """Creates the job according to the input parameter.

            Args:
                job_name {string} -- Name of the job.

            Returns:
                Job object -- Appropriate job depending on the input.
            """
        if job_name == 'ftp':
            return FTPJob(self._storage_resource)
        elif job_name == 'listcat':
            return ListcatJob(self._storage_resource)
        elif job_name == 'migration':
            return MigrationJob(self._storage_resource)
        else:
            return None