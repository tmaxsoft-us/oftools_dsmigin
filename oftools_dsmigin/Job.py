#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module is common for all Job modules in this program.

    Typical usage example:
        job = Job(storage_resource)
        job.run()
    """

# Generic/Built-in modules

# Third-party modules

# Owned modules


class Job(object):
    """A class used to store common values and execute common methods to all type of jobs.

        Attributes:
            _storage_resource {Storage Resource object} -- Object where the program read and write the data. It could be a CSV file or a database table.

        Methods:
            __init__(storage_resource) -- Initializes all attributes of the class.
        """

    def __init__(self, storage_resource):
        """Initializes the only attribute of the class.
            """
        self._storage_resource = storage_resource