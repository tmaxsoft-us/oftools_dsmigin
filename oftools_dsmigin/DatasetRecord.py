#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This modules runs a few methods to manage the dataset records.
"""

# Generic/Built-in modules
import re

# Third-party modules

# Owned modules
from .enums.MigrationEnum import MCol
from .enums.MessageEnum import LogM
from .Log import Log


class DatasetRecord():
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
        for index, value in enumerate(columns):
            self._columns[index] = re.sub(r"[\n\t\s]*", "", value)

    def format(self, widths):
        """Formats CSV record adding trailing spaces to each columns.

        To ease reading and analyzing the file the columns are properly aligned based on an enumeration listing the width for each column.

        Arguments:
            record {list} -- CSV record to be formatted.

        Returns:
            list -- Formatted CSV record.
        """
        record_formatted = []

        Log().logger.debug(LogM.FORMAT_RECORD.value %
                           self._columns[MCol.DSN.value])

        for index, value in enumerate(self._columns):
            if len(value) < widths[index]:
                record_formatted.append(value.ljust(widths[index]))
            else:
                record_formatted.append(value)

        return record_formatted
