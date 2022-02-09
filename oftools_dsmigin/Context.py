#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set of variables and parameters for program execution.

    This module gathers a set of execution parameters which are useful in many other modules. When a 
    parameter is widely used in different modules, a general version of it is created and 
    can be found here.

    Typical usage example:
        Context().tag = args.tag
        Context().clear_all()
    """

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
            _initialization {boolean} --
            _max_datasets {integer} -- The number of datasets to process in the current execution of oftools_dsmigin.
            _tag {string} -- The tag option specified by the user.

            _conversion_directory {string} -- Absolute path of the conversion directory, located under the working directory. It contains all converted datasets that are cleared after each migration (useless files).
            _copybooks_directory {string} -- Absolute path of the copybooks directory, located under the working directory.
            _csv_backups_directory {string} --
            _datasets_directory {string} -- Absolute path of the datasets directory, located under the working directory. It contains all the downloaded datasets.
            _listcat_directory {string} --
            _log_directory {string} -- Absolute path of the log directory, located under the working directory. It contains the logs of each execution of oftools_dsmigin.
            _working_directory {string} -- Absolute path of the working directory.

            _records {list} --

            _ip_address {string} -- The ip address of the mainframe to connect to for the Listcat and FTP executions.
            _listcat {Listcat object} --
            _generations {integer} --
            _prefix {string} --

            _enable_column_list {list} --
            _conversion {string} -- If the user specifies the conversion flag, it changes from '' to '-C' to perform conversion only migration type.
            _encoding_code {string} -- It specifies to what ASCII characters the EBCDIC two-byte data should be converted.
            _force {string} -- If the user specifies the force flag, it changes from '' to '-F' to perform forced migration, which means erasing the dataset if already migrated in OpenFrame.

            _full_timestamp {string} -- The date of today respecting a certain format, including date and time.
            _timestamp {string} -- The date of today respecting a certain format, including date only.
            _init_pwd {string} -- The absolute path to the directory where the command has been executed.

        Methods:
            __init__() -- Initializes all attributes of the context.
            clear_all() -- Clears context completely at the end of the program execution.
        """

    def __init__(self):
        """Initializes all attributes of the context.
            """
        # Required variables for program execution
        self._initialization = False
        self._max_datasets = 0
        self._tag, _, _ = Utils().execute_shell_command('logname')
        self._tag = '_' + self._tag.replace('\n', '')

        # Directories
        self._conversion_directory = ''
        self._copybooks_directory = ''
        self._csv_backups_directory = ''
        self._datasets_directory = ''
        self._listcat_directory = ''
        self._log_directory = ''
        self._working_directory = ''

        # Storage resource records
        self._records = []

        # Input parameters - different jobs
        self._ip_address = None
        self._listcat = None
        self._generations = 0
        self._prefix = ''

        self._enable_column_list = []
        self._conversion = ''
        self._test = ''
        self._encoding_code = ''
        self._force = ''

        # Other
        self._full_timestamp = datetime.datetime.today().strftime(
            '%Y%m%d_%H%M%S')
        self._timestamp = datetime.datetime.today().strftime('%Y-%m-%d')
        self._init_pwd = os.getcwd()

    @property
    def initialization(self):
        """Getter method for the attribute _initialization.

            Returns:
                boolean -- the value for _initialization.
            """
        return self._initialization

    @initialization.setter
    def initialization(self, initialization):
        """Setter method for the attribute _initialization.
            """
        if initialization is not None:
            self._initialization = initialization

    @property
    def max_datasets(self):
        """Getter method for the attribute _max_datasets.

            Returns:
                integer -- the value for _max_datasets.
            """
        return self._max_datasets

    @max_datasets.setter
    def max_datasets(self, max_datasets):
        """Setter method for the attribute _max_datasets.

            Raises:
                SystemError -- Exception is raised if max_datasets is negative.
            """
        try:
            if max_datasets is not None:
                if max_datasets > 0:
                    self._max_datasets = max_datasets
                else:
                    raise SystemError()
        except SystemError:
            Log().logger.critical(
                'SignError: Invalid -n, --number option: Must be positive')
            sys.exit(-1)

    @property
    def tag(self):
        """Getter method for the attribute _tag.

            Returns:
                string -- the value for _tag.
            """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Setter method for the attribute _tag.
            """
        if tag is not None:
            self._tag = '_' + tag

    @property
    def conversion_directory(self):
        """Getter method for the attribute _conversion_directory.

            Returns:
                string -- the value for _conversion_directory.
            """
        return self._conversion_directory

    @property
    def copybooks_directory(self):
        """Getter method for the attribute _copybooks_directory.
            """
        return self._copybooks_directory

    @property
    def csv_backups_directory(self):
        """Getter method for the attribute _csv_backups_directory.

            Returns:
                string -- the value for _csv_backups_directory.
            """
        return self._csv_backups_directory

    @property
    def datasets_directory(self):
        """Getter method for the attribute _datasets_directory.

            Returns:
                string -- the value for _datasets_directory.
            """
        return self._datasets_directory

    @property
    def listcat_directory(self):
        """Getter method for the attribute _listcat_directory.

            Returns:
                string -- the value for _listcat_directory.
            """
        return self._listcat_directory

    @property
    def log_directory(self):
        """Getter method for the attribute _log_directory.

            Returns:
                string -- the value for _log_directory.
            """
        return self._log_directory

    @property
    def working_directory(self):
        """Getter method for the attribute _working_directory.

            Returns:
                string -- the value for _working_directory.
            """
        return self._working_directory

    @working_directory.setter
    def working_directory(self, working_directory):
        """Setter method for the attribute _working_directory and all its subdirectories.

            Only if the input work directory has been correctly specified, it creates the absolute path to this directory. It also creates the working directory if it does not exist already.
            
            Raises:
                FileNotFoundError -- Exception is raised if the working directory as well as the log (sub)directory do not exist.
                """
        working_directory = os.path.expandvars(working_directory)

        self._working_directory = os.path.abspath(working_directory)
        self._conversion_directory = self._working_directory + '/conversion'
        self._copybooks_directory = self._working_directory + '/copybooks'
        self._csv_backups_directory = self._working_directory + '/csv_backups'
        self._datasets_directory = self._working_directory + '/datasets'
        self._listcat_directory = self._working_directory + '/listcat'
        self._log_directory = self._working_directory + '/log'

        if self._initialization:
            Log().logger.info('[context] Initializing working directory')
            Utils().create_directory(self._working_directory)
            Utils().create_directory(self._conversion_directory)
            Utils().create_directory(self._copybooks_directory)
            Utils().create_directory(self._csv_backups_directory)
            Utils().create_directory(self._datasets_directory)
            Utils().create_directory(self._listcat_directory)
            Utils().create_directory(self._log_directory)

        try:
            if os.path.isdir(self._working_directory) is True:
                if os.path.isdir(self._log_directory) is True:
                    Log().logger.debug(
                        '[context] Proper dataset migration working directory specified. Proceeding'
                    )
                else:
                    raise FileNotFoundError()
            else:
                raise FileNotFoundError()
        except FileNotFoundError:
            Log().logger.critical(
                'FileNotFoundError: Please initialize the working directory with the --init option: Not a dataset migration working directory:'
                + working_directory)
            sys.exit(-1)

    @property
    def records(self):
        """Getter method for the attribute _records.

            Returns:
                list -- the value for _records.
            """
        return self._records

    @property
    def ip_address(self):
        """Getter method for the attribute _ip_address.

            Returns:
                string -- the value for _ip_address.
            """
        return self._ip_address

    @ip_address.setter
    def ip_address(self, ip_address):
        """Setter method for the attribute _ip_address.

            Raises:
            SystemError -- Exception is raised if the ip address specified does not respect a correct IPv4 or IPv6 format.
            """
        try:
            if ip_address is not None:
                # Analyze if the argument ip_address respect a valid format
                status = Utils().analyze_ip_address(ip_address)
                if status is True:
                    Log().logger.debug(
                        '[context] Proper ip address specified. Proceeding')
                    self._ip_address = ip_address
                else:
                    raise SystemError()
        except SystemError:
            Log().logger.critical(
                'FormatError: Invalid -i, --ip-address option: Must respect either IPv4 or IPv6 standard format'
            )
            sys.exit(-1)

    @property
    def listcat(self):
        """Getter method for the attribute _listcat.

            Returns:
                Listcat object -- the value for _listcat
            """
        return self._listcat

    @listcat.setter
    def listcat(self, listcat):
        """Setter method for the attribute _listcat.
            """
        if listcat is not None:
            self._listcat = listcat

            rc = self._listcat.read_csv()
            if rc != 0:
                Log().logger.warning(
                    '[listcat] Skipping listcat file data retrieval for VSAM datasets'
                )
                self._listcat = {}

    @property
    def generations(self):
        """Getter method for the attribute _generations.

            Returns:
                integer -- the value for _generations.
            """
        return self._generations

    @generations.setter
    def generations(self, generations):
        """Setter method for the attribute _generations.

            Raises:
                SystemError -- Exception is raised if generations is negative.
            """
        try:
            if generations is not None:
                if generations > 0:
                    self._generations = generations
                else:
                    raise SystemError()
        except SystemError:
            Log().logger.critical(
                'SignError: Invalid -g, --generations option: Must be positive')
            sys.exit(-1)

    @property
    def prefix(self):
        """Getter method for the attribute _prefix.

            Returns:
                string -- the value for _prefix.
            """
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        """Setter method for the attribute _prefix.
            """
        if prefix is not None:
            self._prefix = prefix + '.'

    @property
    def enable_column_list(self):
        """Getter method for the attribute _enable_column_list.

            Returns:
                list -- the value for _enable_column_list.
            """
        return self._enable_column_list

    @enable_column_list.setter
    def enable_column_list(self, column_names):
        """Setter method for the attribute _enable_column_list.
            """
        if column_names is not None:
            columns = column_names.split(':')
            for column in columns:
                self._enable_column_list.append(column)

    @property
    def conversion(self):
        """Getter method for the attribute _conversion.

            Returns:
                string -- the value for _conversion.
            """
        return self._conversion

    @conversion.setter
    def conversion(self, conversion):
        """Setter method for the attribute _conversion.
            """
        if conversion is not None:
            if conversion is True:
                self._conversion = ' -C '

    @property
    def test(self):
        """Getter method for the attribute _test.

            Returns:
                string -- the value for _test.
            """
        return self._test

    @test.setter
    def test(self, test):
        """Setter method for the attribute _test.
            """
        if test is not None:
            if test is True:
                self._conversion = ' -C '
                self._test = test

    @property
    def encoding_code(self):
        """Getter method for the attribute _encoding_code.

            Returns:
                string -- the value for _encoding_code.
            """
        return self._encoding_code

    @encoding_code.setter
    def encoding_code(self, encoding_code):
        """Setter method for the attribute _encoding_code.
            """
        if encoding_code is not None:
            self._encoding_code = encoding_code
    
    @property
    def force(self):
        """Getter method for the attribute _force.

            Returns:
                string -- the value for _force.
            """
        return self._force

    @force.setter
    def force(self, force):
        """Setter method for the attribute _force.
            """
        if force is not None:
            if force is True:
                self._force = ' -F '

    @property
    def full_timestamp(self):
        """Getter method for the attribute _full_timestamp.

            Returns:
                string -- the value for _full_timestamp.
            """
        return self._full_timestamp

    @property
    def timestamp(self):
        """Getter method for the attribute _timestamp.

            Returns:
                string -- the value for _timestamp.
            """
        return self._timestamp

    def clear_all(self):
        """Clears context completely at the end of the program execution.
            """
        os.chdir(self._init_pwd)
