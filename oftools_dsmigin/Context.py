#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set of variables and parameters for program execution.

This module gathers a set of execution parameters which are useful in many other modules. When a 
parameter is widely used in different modules, a general version of it is created and 
can be found here.

Typical usage example:
  Context().tag = args.tag
"""

# Generic/Built-in modules
import datetime
import os
import sys

# Third-party modules

# Owned modules
from .Log import Log


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
        _input_csv: A string, the name of the input CSV file.
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
        __init__(): Initializes all attributes of the context.
    """

    def __init__(self):
        """Initializes all attributes of the context.
        """
        self._input_csv = ''
        self._migration_type = ''
        self._encoding_code = ''
        self._number = 0
        self._ip_address = ''
        self._listcat_result = ''
        self._tag = ''
        self._today_date = ''

        # Directories
        self._conversion_directory = ''
        self._copybook_directory = ''
        self._dataset_directory = ''
        self._log_directory = ''
        self._working_directory = ''

        # Other
        self._init_pwd = os.getcwd()

    @property
    def input_csv(self):
        """Getter method for the attribute _input_csv.
        """
        return self._input_csv

    @input_csv.setter
    def input_csv(self, input_csv):
        """Setter method for the attribute _input_csv.
        """
        if input_csv is not None:
            #TODO update this path that might cause an issue if the csv specified by the user is already absolute path
            self._input_csv = os.getcwd() + '/' + input_csv

    @property
    def migration_type(self):
        """Getter method for the attribute _migration_type.
        """
        return self._migration_type

    @migration_type.setter
    def migration_type(self, migration_type):
        """Setter method for the attribute _migration_type.
        """
        if migration_type is not None:
            self._migration_type = migration_type

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
    def number(self):
        """Getter method for the attribute _number. 
        
        Number of datasets to download in the current execution.
        """
        return self._number

    @number.setter
    def number(self, number):
        """Setter method for the attribute _number.
        """
        if number is not None:
            self._number = number

    @property
    def ip_address(self):
        """Getter method for the attribute _ip_address.
        
        Mainframe server.
        """
        return self._ip_address

    @ip_address.setter
    def ip_address(self, ip_address):
        """Setter method for the attribute _ip_address.
        """
        if ip_address is not None:
            self._ip_address = ip_address

    @property
    def listcat_result(self):
        """Getter method for the attribute _listcat_result.
        
        text file(s) containing the listcat command result.
        """
        return self._listcat_result

    @listcat_result.setter
    def listcat_result(self, listcat_result):
        """Setter method for the attribute _listcat_result.

        It first analyzes if the listcat_result has been specified and create an absolute path if necessary. Then it analyzes if the listcat result specified is a directory or a file, and creates the actual listcat_result list used for the execution of the program.
        """
        if listcat_result is not None and not listcat_result.startswith('/'):
            path_to_listcat = os.getcwd() + '/' + listcat_result
        else:
            path_to_listcat = listcat_result

        if os.path.isdir(path_to_listcat):
            directory = os.path.expandvars(path_to_listcat)
            listcat_list = []
            for root, _, files in os.walk(directory):
                if root.startswith('.'):
                    continue
                for filename in files:
                    if filename.startswith('.'):
                        continue
                    listcat_list.append(os.path.abspath(os.path.join(root,
                                                                    filename)))
        else:
            listcat_list = [path_to_listcat]

        self._listcat_result = listcat_list

    @property
    def tag(self):
        """Getter method for the attribute tag.
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Setter method for the attribute tag.
        """
        if tag is not None:
            self._tag = '_' + tag

    @property
    def today_date(self):
        """Getter method for the attribute _today_date.
        """
        return self._today_date

    @today_date.setter
    def today_date(self):
        """Setter method for the attribute _today_date.

        Set the date of today following a specific format.
        """
        today = datetime.datetime.today()
        self._today_date = today.strftime('%Y-%m-%d')
    
    @property
    def conversion_directory(self):
        """Getter method for the attribute _conversion_directory.

        converted datasets directory location
        """
        return self._conversion_directory

    @conversion_directory.setter
    def conversion_directory(self):
        """Setter method for the _conversion_directory.

        Create the directory if it does not already exists.
        """
        try:
            self._conversion_directory = self._working_directory + '/conversion'
            if not os.path.exists(self._conversion_directory):
                os.mkdirs(self._conversion_directory)
        except:
            print(
                'Dataset conversion directory creation failed. Permission denied.'
            )
    
    @property
    def copybook_directory(self):
        """Getter method for the attribute _copybook_directory.
        """
        return self._copybook_directory

    @copybook_directory.setter
    def copybook_directory(self, copybook_directory):
        """Setter method for the attribute _copybook_directory.
        """
        if copybook_directory is not None and not copybook_directory.startswith('/'):
            self._copybook_directory = os.getcwd() + '/' + copybook_directory
        else:
            self._copybook_directory = copybook_directory

    @property
    def dataset_directory(self):
        """Getter method for the attribute _dataset_directory.
        """
        return self._dataset_directory

    @dataset_directory.setter
    def dataset_directory(self):
        """Setter method for the attribute _dataset_directory.

        Create the directory if it does not already exists.
        """
        try:
            self._dataset_directory = self._working_directory + '/datasets'
            if not os.path.exists(self._dataset_directory):
                os.mkdirs(self._dataset_directory)
        except:
            print('Dataset directory creation failed. Permission denied.')

    @property
    def log_directory(self):
        """Getter method for the attribute _log_directory.
        """
        return self._log_directory

    @log_directory.setter
    def log_directory(self):
        """Setter method for the attribute _log_directory.

        Create the directory if it does not already exists.
        """
        try:
            self._log_directory = self._working_directory + '/logs'
            if not os.path.exists(self._log_directory):
                os.mkdirs(self._log_directory)
        except:
            print('Logs directory creation failed. Permission denied.')

    @property
    def working_directory(self):
        """Getter method for the attribute _working_directory.
        """
        return self._working_directory

    @working_directory.setter
    def working_directory(self, working_directory):
        """Setter method for the attribute _working_directory.

        Only if the input work directory has been correctly specified, it creates the absolute path to this directory. It also creates the working directory if it does not exist already.
        """
        working_directory = os.path.expandvars(working_directory)

        if os.path.isdir(working_directory) and os.access(
                        working_directory, os.W_OK):
            # Save work directory to Context
            self._working_directory = os.path.abspath(working_directory)
            os.chdir(working_directory)
        else:
            Log().logger.critical(
                'PermissionError: Permission denied: No write access on working directory: '
                + working_directory)
            sys.exit(-1)

    def clear_all(self):
        """Clears context completely at the end of the program execution.
        """
        os.chdir(self._init_pwd)
