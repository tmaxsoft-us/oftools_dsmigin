#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enumerate columns used in the listcat and migration CSV files, as
well as the width of each column.

Typical usage example:
  records[Col.DSN.name] = "DSN"
  records[Col.DSN.value] = 0
"""

# Generic/Built-in modules
import enum

# Third-party modules
import aenum

# Owned modules


@enum.unique
class LCol(enum.Enum):
    """List column names and indexes in the listcat CSV file.
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


@enum.unique
class MCol(enum.Enum):
    """List column names and indexes used in the migration CSV file.
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


class Width(aenum.Enum):
    """List column widths.
    """
    _settings_ = aenum.NoAlias

    DSN = 45
    COPYBOOK = 10
    RECFM = 5
    LRECL = 5
    BLKSIZE = 8
    DSORG = 5
    VOLSER = 8
    CATALOG = 18
    VSAM = 4
    KEYOFF = 6
    KEYLEN = 6
    MAXLRECL = 8
    AVGLRECL = 8
    CISIZE = 8
    IGNORE = 6
    LISTCAT = 7
    LISTCATDATE = 11
    FTP = 3
    FTPDATE = 8
    FTPTIME = 8
    DSMIGIN = 7
    DSMIGINDATE = 11
    DSMIGINTIME = 11
