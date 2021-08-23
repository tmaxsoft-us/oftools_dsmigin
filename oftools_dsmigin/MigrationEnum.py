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
    VSAM = 7
    KEYOFF = 8
    KEYLEN = 9
    MAXLRECL = 10
    AVGLRECL = 11
    CISIZE = 12
    IGNORE = 13
    LISTCAT = 14
    LISTCATDATE = 15
    FTP = 16
    FTPDATE = 17
    FTPDURATION = 18
    DSMIGIN = 19
    DSMIGINDATE = 20
    DSMIGINDURATION = 21
    # TODO Catalog column