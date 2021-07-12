#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set of parameters useful in any module.

This module gathers a set of execution parameters that are useful in many other modules. When a 
parameter is widely used in different modules, a general version of it is created and 
can be found here.

Typical usage example:

  Context().get_input_csv()
"""

# Generic/Built-in modules
import datetime
import os

# Third-party modules

# Owned modules


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Context(metaclass=SingletonMeta):
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
        _work_directory: A string, working directory for the program execution.
        _dataset_directory: A string, located under the working directory, this directory contains all downloaded datasets.
        _conversion_directory: A string, located under the working directory, this directory contains all converted datasets 
            that are cleared after each migration (useless files).
        _copybook_directory: A string, the location of the copybook directory tracked with git.
        _log_directory: A string, located under the working directory, this directory contains the logs of each execution of 
            oftools_dsmigin.

    Methods:
        __init__(): Initializes all attributes of the context.
        get_input_csv(): Getter method for the input CSV file.
        set_input_csv(input_csv): Setter method for the input CSV file.
        get_migration_type(): Getter method for the migration type.
        set_migration_type(migration_type): Setter method for the migration type.
        get_encoding_code(): Getter method for the encoding code for the migration.
        set_encoding_code(encoding_code): Setter method for the encoding code for the migration.
        get_number(): Getter method for the number of datasets to download in the current execution.
        set_number(number): Setter method for the number of datasets to download in the current execution.
        get_ip_address(): Getter method for the IP address of the mainframe server.
        set_ip_address(ip_address): Setter method for the IP address of the mainframe server.
        get_listcat_result(): Getter method for the text file(s) containing the listcat command result.
        set_listcat_result(listcat_result): Setter method for the text file(s) containing the listcat command result.
        get_tag(): Getter method for the tag input from the user.
        set_tag(tag): Setter method for the tag input from the user.
        get_today_date(): Getter method for the date of today.
        set_today_date(): Setter method for the date of today.
        get_work_directory(): Getter method for the work directory location.
        set_work_directory(work_directory): Setter method for the work directory location.
        get_dataset_directory(): Getter method for the dataset directory location, under the work directory.
        set_dataset_directory(): Setter method for the dataset directory location, under the work directory.
        get_conversion_directory(): Getter method for the converted datasets directory location, under the work directory.
        set_conversion_directory(): Setter method for the converted datasets directory location, under the work directory.
        get_copybook_directory(): Getter method for the copybook directory location.
        set_copybook_directory(): Setter method for the copybook directory location.
        get_log_directory(): Getter method for the log directory location, under the work directory.
        set_log_directory(): Setter method for the log directory location, under the work directory.
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
        self._work_directory = ''
        self._dataset_directory = ''
        self._conversion_directory = ''
        self._copybook_directory = ''
        self._log_directory = ''

    def get_input_csv(self):
        """Getter method for the input CSV file.
        """
        return self._input_csv

    def set_input_csv(self, input_csv):
        """Setter method for the input CSV file.

        Only if the input CSV file has been correctly specified, it creates the absolute path to the CSV file.
        """
        if input_csv is not None:
            self._input_csv = os.getcwd() + '/' + input_csv

    def get_migration_type(self):
        """Getter method for the migration type.
        """
        return self._migration_type

    def set_migration_type(self, migration_type):
        """Setter method for the migration type.
        """
        if migration_type is not None:
            self._migration_type = migration_type

    def get_encoding_code(self):
        """Getter method for the encoding code for the migration.
        """
        return self._encoding_code

    def set_encoding_code(self, encoding_code):
        """Setter method for the encoding code for the migration.
        """
        if encoding_code is not None:
            self._encoding_code = encoding_code

    def get_number(self):
        """Getter method for the number of datasets to download in the current execution.
        """
        return self._number

    def set_number(self, number):
        """Setter method for the number of datasets to download in the current execution.
        """
        if number is not None:
            self._number = number

    def get_ip_address(self):
        """Getter method for the IP address of the mainframe server.
        """
        return self._ip_address

    def set_ip_address(self, ip_address):
        """Setter method for the IP address of the mainframe server.
        """
        if ip_address is not None:
            self._ip_address = ip_address

    def get_listcat_result(self):
        """Getter method for the text file(s) containing the listcat command result.
        """
        return self._listcat_result

    def set_listcat_result(self, listcat_result):
        """Setter method for the text file(s) containing the listcat command result.

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

    def get_tag(self):
        """Getter method for the tag input from the user.
        """
        return self._tag

    def set_tag(self, tag):
        """Setter method for the tag input from the user.
        """
        if tag is not None:
            self._tag = tag

    def get_today_date(self):
        """Getter method for the date of today.
        """
        return self._today_date

    def set_today_date(self):
        """Setter method for the date of today.

        Set the date of today following a specific format.
        """
        today = datetime.datetime.today()
        self._today_date = today.strftime('%Y-%m-%d')

    def get_work_directory(self):
        """Getter method for the work directory location.
        """
        return self._work_directory

    def set_work_directory(self, work_directory):
        """Setter method for the work directory location.

        Only if the input work directory has been correctly specified, it creates the absolute path to this directory. It also creates the working directory if it does not exist already.
        """
        if work_directory is not None and not work_directory.startswith('/'):
            self._work_directory = os.getcwd() + '/' + work_directory
        else:
            self._work_directory = work_directory

        try:
            if not os.path.exists(self._work_directory):
                os.mkdirs(self._work_directory)
        except:
            print('Working directory creation failed. Permission denied.')

    def get_dataset_directory(self):
        """Getter method for the dataset directory location, under the work directory.
        """
        return self._dataset_directory

    def set_dataset_directory(self):
        """Setter method for the dataset directory location, under the work directory.

        Create the directory if it does not already exists.
        """
        try:
            self._dataset_directory = self._work_directory + '/datasets'
            if not os.path.exists(self._dataset_directory):
                os.mkdirs(self._dataset_directory)
        except:
            print('Dataset directory creation failed. Permission denied.')

    def get_conversion_directory(self):
        """Getter method for the converted datasets directory location, under the work directory.
        """
        return self._conversion_directory

    def set_conversion_directory(self):
        """Setter method for the converted datasets directory location, under the work directory.

        Create the directory if it does not already exists.
        """
        try:
            self._conversion_directory = self._work_directory + '/conversion'
            if not os.path.exists(self._conversion_directory):
                os.mkdirs(self._conversion_directory)
        except:
            print(
                'Dataset conversion directory creation failed. Permission denied.'
            )

    def get_copybook_directory(self):
        """Getter method for the copybook directory location.
        """
        return self._copybook_directory

    def set_copybook_directory(self, copybook_directory):
        """Setter method for the copybook directory location.
        """
        if copybook_directory is not None and not copybook_directory.startswith('/'):
            self._copybook_directory = os.getcwd() + '/' + copybook_directory
        else:
            self._copybook_directory = copybook_directory

    def get_log_directory(self):
        """Getter method for the log directory location, under the work directory.
        """
        return self._log_directory

    def set_log_directory(self):
        """Setter method for the log directory location, under the work directory.

        Create the directory if it does not already exists.
        """
        try:
            self._log_directory = self._work_directory + '/logs'
            if not os.path.exists(self._log_directory):
                os.mkdirs(self._log_directory)
        except:
            print('Logs directory creation failed. Permission denied.')
