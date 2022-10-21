#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set of methods useful in any module.

This module gathers a set of methods that are useful in all Listcat related
modules. When a method is widely used in different modules, a general version
of it is created and can be found here.

Typical usage example:
  ListcatHandler().get_migrated(record, "listcat", ip_address)
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from ..enums.Message import LogM
from ..enums.CSV import MCol
from ..Log import Log
from .ShellHandler import ShellHandler


class SingletonMeta(type):
    """This pattern restricts the instantiation of a class to one object.

    It is a type of creational pattern and involves only one class to create
    methods and specified objects. It provides a global point of access to the
    instance created.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ListcatHandler(metaclass=SingletonMeta):
    """A class used to run .

    Methods:
        get_migrated(record, job_name, ip_address, n) -- Executes the FTP
            commands on Mainframe to retrieve dataset info in the case of VOLSER set to Migrated.
        update_record(record, fields) -- Updates a dataset migration record.
    """

    @staticmethod
    def get_migrated(record, job_name, ip_address, n=1):
        """Executes the FTP commands on Mainframe to retrieve dataset info in
        the case of VOLSER set to Migrated.

        Arguments:
            record {list} -- Dataset migration record.

        Returns:
            list -- The new list of parameters extracted from the FTP command after the recall.
        """
        fields = []
        record[MCol.VOLSER.value] = "Migrated"

        Log().logger.info(LogM.MIGRATED.value % job_name)
        _, _, status = ShellHandler().ftp_recall(record[MCol.DSN.value], job_name,
                                             ip_address)

        if status != 0:
            return fields

        Log().logger.debug(LogM.FTP_LS_AGAIN.value % job_name)
        stdout, _, status = ShellHandler().ftp_ls(record[MCol.DSN.value],
                                                  job_name, ip_address)

        if status == 0:
            lines = stdout.splitlines()
            if len(lines) > 1:
                fields = lines[n].split()
            else:
                Log().logger.error(LogM.FTP_EMPTY.value % job_name)

        return fields

    @staticmethod
    def process_tape(record, fields, job_name):
        """
        """
        Log().logger.info(LogM.TAPE.value % job_name)
        record[MCol.VOLSER.value] = fields[1]

    @staticmethod
    def update_record(record, fields):
        """Updates a dataset migration record.

        Arguments:
            record {list} -- Dataset migration record.
            fields {list} -- Dataset parameters extracted from FTP command or
                file.
        """
        record[MCol.RECFM.value] = fields[-5]
        record[MCol.LRECL.value] = fields[-4]
        record[MCol.BLKSIZE.value] = fields[-3]
        record[MCol.DSORG.value] = fields[-2]
        record[MCol.VOLSER.value] = fields[0]
