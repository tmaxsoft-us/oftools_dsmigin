#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module handles the enumeration of all the column names for the migration CSV file.

    Typical usage example:
      records[Col.DSN.name] = 'DSN'
      records[Col.DSN.value] = 0"""

# Generic/Built-in modules
import enum

# Third-party modules

# Owned modules


@enum.unique
class Col(enum.Enum):
    """Just an enumeration of all the columns we need in the migration CSV file.
        """
    DSN = 0
    COPYBOOK = 1
    RECFM = 2
    LRECL = 3
    BLKSIZE = 4
    DSORG = 5
    VOLSER = 6
    CATALOG = 7
    VSAM = 8
    KEYOFF = 9
    KEYLEN = 10
    MAXLRECL = 11
    AVGLRECL = 12
    CISIZE = 13
    IGNORE = 14
    LISTCAT = 15
    LISTCATDATE = 16
    FTP = 17
    FTPDATE = 18
    FTPDURATION = 19
    DSMIGIN = 20
    DSMIGINDATE = 21
    DSMIGINDURATION = 22