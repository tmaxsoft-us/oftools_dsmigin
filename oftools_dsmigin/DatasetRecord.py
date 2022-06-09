#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This modules runs a few methods to manage the dataset records.
"""

# Generic/Built-in modules
import re

# Third-party modules

# Owned modules


class DatasetRecord(object):
    """A class used just as a dataset record object, with one attribute being the columns.

    Attributes:
        _columns {list} -- Record columns, filled by the data coming from the CSV file.
    
    Methods:
        __init__(columns) -- Initializes the only attribute of the class.
    """

    def __init__(self, columns):
        """Initializes the only attribute of the class.
        """
        self._columns = ['' for _ in range(len(columns))]

    @property
    def columns(self):
        """Getter method for the attribute _columns.
        """
        return self._columns

    @columns.setter
    def columns(self, columns):
        """Setter method for the attribute _columns.
        """
        for i in range(len(columns)):
            self._columns[i] = re.sub(r"[\n\t\s]*", "", columns[i])
