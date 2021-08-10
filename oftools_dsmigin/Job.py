#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Common module for all Job modules in this program.

    Typical usage example:"""

# Generic/Built-in modules

# Third-party modules

# Owned modules


class Job(object):
    """
        """

    def __init__(self, storage_resource):
        """Initializes the class with all the attributes.
            """
        self._number_downloaded = 0
        self._number_migrated = 0
        self._storage_resource = storage_resource