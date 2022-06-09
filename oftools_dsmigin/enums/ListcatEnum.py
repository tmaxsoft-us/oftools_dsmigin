#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module handles the enumeration of all the column names for the listcat CSV file.

Typical usage example:
    records[LCol.DSN.name] = 'DSN'
    records[LCol.DSN.value] = 0
"""

# Generic/Built-in modules
import enum

# Third-party modules

# Owned modules


@enum.unique
class LCol(enum.Enum):
    """Just an enumeration of all the columns we need in the listcat CSV file.
    """
    DSN = 0
    RECFM = 1
    VSAM = 2
    KEYOFF = 3
    KEYLEN = 4
    MAXLRECL = 5
    AVGLRECL = 6
    CISIZE = 7
    CATALOG = 8