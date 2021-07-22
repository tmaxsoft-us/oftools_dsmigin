#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .MigrationEnum import Col

class DatasetRecord(object):
    """
        """
    
    def __init__(self):
        """
            """
        self._columns = ['' for _ in range(len(Col))]

    @property
    def columns(self):
        """
            """
        return self._columns

    @columns.setter
    def columns(self, columns):
        """
            """
        for i in range(len(columns)):
            self._columns[i] = columns[i].replace(' ','')
