#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module is common for all Job modules in this program.

Typical usage example:
  job = Job()
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules


class Job(object):
    """A class used to store common values and execute common methods to all types of jobs.

    Attributes:
        _name {string} -- Name of the job.

    Methods:
        __init__() -- Initializes the class with all the attributes.
    """

    def __init__(self, name):
        """Initializes the class with all the attributes.
        """
        self._name = name
