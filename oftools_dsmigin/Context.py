#!/usr/bin/env python
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
        self._ftp_type = ''
        self._ip_address = ''
        self._number_datasets = 0

        self._listcat_file_path = ''

        self._encoding_code = ''
        self._migration_type = ''

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
        self._timestamp = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
        self._init_pwd = os.getcwd()

    @property
    def ftp_type(self):
        """Getter method for the attribute _ftp_type.
            """
        return self._ftp_type

    @ftp_type.setter
    def ftp_type(self, ftp):
        """Setter method for the attribute _ftp_type.
            """
        if ftp is not None:
            self._ftp_type = ftp

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
    def listcat_file_path(self):
        """Getter method for the attribute _listcat_file_path.
            """
        return self._listcat_file_path

    @listcat_file_path.setter
    def listcat_file_path(self, listcat):
        """Setter method for the attribute _listcat_result.

            It first analyzes if the listcat_result has been specified and create an absolute path if necessary. Then it analyzes if the listcat result specified is a directory or a file, and creates the actual listcat_result list used for the execution of the program."""
        if listcat is not None and not listcat.startswith('/'):
            path_to_listcat = os.getcwd() + '/' + listcat
        else:
            path_to_listcat = listcat

        if os.path.isdir(path_to_listcat):
            directory = os.path.expandvars(path_to_listcat)
            listcat_list = []
            for root, _, files in os.walk(directory):
                if root.startswith('.'):
                    continue
                for filename in files:
                    if filename.startswith('.'):
                        continue
                    listcat_list.append(
                        os.path.abspath(os.path.join(root, filename)))
        else:
            listcat_list = [path_to_listcat]

        self._listcat_file_path = listcat_list

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
    def migration_type(self):
        """Getter method for the attribute _migration_type.
            """
        return self._migration_type

    @migration_type.setter
    def migration_type(self, migration):
        """Setter method for the attribute _migration_type.
            """
        if migration is not None:
            self._migration_type = migration

    @property
    def conversion_directory(self):
        """Getter method for the attribute _conversion_directory.
            """
        return self._conversion_directory

    def set_conversion_directory(self):
        """Setter method for the attribute _conversion_directory.
            """
        self._conversion_directory = self._working_directory + '/dataset_converted'
        Utils().create_directory(self._conversion_directory)

    @property
    def copybook_directory(self):
        """Getter method for the attribute _copybook_directory.
            """
        return self._copybook_directory

    @copybook_directory.setter
    def copybook_directory(self, copybook_directory):
        """Setter method for the attribute _copybook_directory.
            """
        if copybook_directory is not None and not copybook_directory.startswith(
                '/'):
            self._copybook_directory = os.getcwd() + '/' + copybook_directory
        else:
            self._copybook_directory = copybook_directory

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

    def set_dataset_directory(self):
        """Setter method for the attribute _dataset_directory.
            """
        self._dataset_directory = self._working_directory + '/dataset_download'
        Utils().create_directory(self._dataset_directory)

    @property
    def listcat_directory(self):
        """Getter method for the attribute _listcat_directory.
            """
        return self._listcat_directory

    def set_listcat_directory(self):
        """Setter method for the attribute _listcat_directory.
            """
        self._listcat_directory = self._working_directory + '/listcat'
        Utils().create_directory(self._listcat_directory)

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

        if os.path.isdir(working_directory) and os.access(
                working_directory, os.W_OK):
            # Save absolute path to work directory to Context
            self._working_directory = os.path.abspath(working_directory)
            os.chdir(working_directory)

            self._csv_backup_directory = self._working_directory + '/csv_backups'
            Utils().create_directory(self._csv_backup_directory)

            self._log_directory = self._working_directory + '/log'
            Utils().create_directory(self._log_directory)
        else:
            Log().logger.critical(
                'PermissionError: Permission denied: No write access on working directory: '
                + working_directory)
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
    def timestamp(self):
        """Getter method for the attribute _timestamp.
            """
        return self._timestamp

    def clear_all(self):
        """Clears context completely at the end of the program execution.
            """
        os.chdir(self._init_pwd)
