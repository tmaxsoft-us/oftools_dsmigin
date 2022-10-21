#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common module for all Job modules in this program.

Typical usage example:
  job = Job()
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules


class Job():
    """Store common values and execute common methods to all types of jobs.

    Attributes:
        _name {string} -- Name of the job.

    Methods:
        __init__() -- Initialize the class with its attributes.
    """

    def __init__(self, name):
        """Initialize the class with its attributes.
        """
        self._name = name
