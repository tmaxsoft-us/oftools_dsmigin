#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set of variables and parameters for program execution.

    This module gathers a set of execution parameters which are useful in many other modules. When a 
    parameter is widely used in different modules, a general version of it is created and 
    can be found here.

    Typical usage example:
        Context().tag = args.tag"""

# Generic/Built-in modules
import datetime
import os
import sys

# Third-party modules

# Owned modules
from .Log import Log
from .Utils import Utils


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Context(object, metaclass=SingletonMeta):
    """A class used as a parameter library for the execution of the program.

        Attributes:
            _migration_type: A string, either 'C' or 'G' for generation or conversion only migration type.
            _encoding_code: A string, specifies to what ASCII characters the EBCDIC two-byte data should be converted.
            _number: An integer, the number of datasets to download in the current execution of oftools_dsmigin.
            _ip_address: A string, the ip address of the mainframe to connect to for the FTP execution.
            _listcat_result: A list, the name of the text file(s) that contains the listcat command result.
            _tag: A string, the tag option used by the user.
            _today_date: A string, the date of today respecting a certain format.

            _conversion_directory: A string, located under the working directory, this directory contains all converted datasets 
                that are cleared after each migration (useless files).
            _copybook_directory: A string, the location of the copybook directory tracked with git.
            _dataset_directory: A string, located under the working directory, this directory contains all downloaded datasets.
            _log_directory: A string, located under the working directory, this directory contains the logs of each execution of 
                oftools_dsmigin.
            _working_directory: A string, working directory for the program execution.

        Methods:
            __init__(): Initializes all attributes of the context."""

    def __init__(self):
        """Initializes all attributes of the context.
            """
        # Input parameters - different jobs
        self._initialization = False

        self._ip_address = ''
        self._number_datasets = 0
        self._prefix = ''

        self._encoding_code = ''
        self._conversion = False

        # Directories
        self._conversion_directory = ''
        self._copybook_directory = ''
        self._csv_backup_directory = ''
        self._dataset_directory = ''
        self._listcat_directory = ''
        self._log_directory = ''
        self._working_directory = ''

        # CSV records data
        self._records = []

        # Other
        self._tag = ''
        self._full_timestamp = datetime.datetime.today().strftime(
            '%Y%m%d_%H%M%S')
        self._timestamp = datetime.datetime.today().strftime('%Y-%m-%d')
        self._init_pwd = os.getcwd()

    @property
    def initialization(self):
        """Getter method for the attribute _initialization.
            """
        return self._initialization

    @initialization.setter
    def initialization(self, initialization):
        """Setter method for the attribute _initialization.
            """
        self._initialization = initialization

    @property
    def ip_address(self):
        """Getter method for the attribute _ip_address.
            """
        return self._ip_address

    @ip_address.setter
    def ip_address(self, ip_address):
        """Setter method for the attribute _ip_address.
            """
        if ip_address is not None:
            self._ip_address = ip_address

    @property
    def number_datasets(self):
        """Getter method for the attribute _number_datasets.
            """
        return self._number_datasets

    @number_datasets.setter
    def number_datasets(self, number):
        """Setter method for the attribute _number_datasets.
            """
        if number is not None:
            self._number_datasets = number

    @property
    def prefix(self):
        """Getter method for the attribute _prefix.
            """
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        """Setter method for the attribute _prefix.
            """
        if prefix is not None:
            self._prefix = prefix + '.'

    @property
    def encoding_code(self):
        """Getter method for the attribute _encoding_code.
            """
        return self._encoding_code

    @encoding_code.setter
    def encoding_code(self, encoding_code):
        """Setter method for the attribute _encoding_code.
            """
        if encoding_code is not None:
            self._encoding_code = encoding_code

    @property
    def conversion(self):
        """Getter method for the attribute _conversion.
            """
        return self._conversion

    @conversion.setter
    def conversion(self, conversion):
        """Setter method for the attribute _conversion.
            """
        self._conversion = conversion

    @property
    def conversion_directory(self):
        """Getter method for the attribute _conversion_directory.
            """
        return self._conversion_directory

    @property
    def copybook_directory(self):
        """Getter method for the attribute _copybook_directory.
            """
        return self._copybook_directory

    @property
    def csv_backup_directory(self):
        """Getter method for the attribute _copybook_directory.
            """
        return self._csv_backup_directory

    @property
    def dataset_directory(self):
        """Getter method for the attribute _dataset_directory.
            """
        return self._dataset_directory

    @property
    def listcat_directory(self):
        """Getter method for the attribute _listcat_directory.
            """
        return self._listcat_directory

    @property
    def log_directory(self):
        """Getter method for the attribute _log_directory.
            """
        return self._log_directory

    @property
    def working_directory(self):
        """Getter method for the attribute _working_directory.
            """
        return self._working_directory

    @working_directory.setter
    def working_directory(self, working_directory):
        """Setter method for the attribute _working_directory and all its subdirectories.

            Only if the input work directory has been correctly specified, it creates the absolute path to this directory. It also creates the working directory if it does not exist already."""
        working_directory = os.path.expandvars(working_directory)
        self._working_directory = os.path.abspath(working_directory)

        self._conversion_directory = self._working_directory + '/conversion'
        self._copybook_directory = self._working_directory + '/copybooks'
        self._csv_backup_directory = self._working_directory + '/csv_backups'
        self._dataset_directory = self._working_directory + '/datasets'
        self._listcat_directory = self._working_directory + '/listcat'
        self._log_directory = self._working_directory + '/log'

        if self._initialization:
            rc = Utils().create_directory(self._working_directory)
            if rc != 0:
                return rc

            Utils().create_directory(self._conversion_directory)
            Utils().create_directory(self._copybook_directory)
            Utils().create_directory(self._csv_backup_directory)
            Utils().create_directory(self._dataset_directory)
            Utils().create_directory(self._listcat_directory)
            Utils().create_directory(self._log_directory)

        try:
            if os.path.isdir(self._working_directory) is False:
                raise FileNotFoundError()
        except FileNotFoundError:
            Log().logger.error(
                'FileNotFoundError: No such file or directory: ' +
                working_directory)
            sys.exit(-1)

    @property
    def records(self):
        """Getter method for the attribute _records.
            """
        return self._records

    @property
    def tag(self):
        """Getter method for the attribute _tag.
            """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Setter method for the attribute _tag.
            """
        if tag is not None:
            self._tag = '_' + tag

    @property
    def full_timestamp(self):
        """Getter method for the attribute _full_timestamp.
            """
        return self._full_timestamp

    @property
    def timestamp(self):
        """Getter method for the attribute _timestamp.
            """
        return self._timestamp

    def clear_all(self):
        """Clears context completely at the end of the program execution.
            """
        os.chdir(self._init_pwd)
