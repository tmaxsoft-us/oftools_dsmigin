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
        _gdg {string} --
        _name {string} --
        _storage_resource {Storage Resource object} -- Object where the program read and write the data. It could be a CSV file or a database table.

    Methods:
        __init__(storage_resource) -- Initializes the class with all the attributes.
    """

    def __init__(self, name, storage_resource):
        """Initializes the class with all the attributes.
        """
        self._gdg = None
        self._name = name
        self._storage_resource = storage_resource
