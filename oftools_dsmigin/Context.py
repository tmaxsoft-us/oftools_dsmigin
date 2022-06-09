#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set of variables and parameters for program execution.

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
from .enums.MessageEnum import ErrorM, LogM
from .handlers.FileHandler import FileHandler
from .handlers.ShellHandler import ShellHandler
from .Log import Log


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Context(object, metaclass=SingletonMeta):
    """A class used to store a set of variables and parameters across all modules for the execution of the program.

    Attributes:
        _init {boolean} --
        _number {integer} -- Number of datasets to process in the current execution of oftools_dsmigin.

        _conversion_directory {string} -- Absolute path of the conversion subdirectory. It contains all converted datasets that are cleared after each migration (useless files).
        _copybooks_directory {string} -- Absolute path of the copybooks subdirectory.
        _csv_backups_directory {string} --
        _datasets_directory {string} -- Absolute path of the datasets subdirectory. It contains all the downloaded datasets.
        _listcat_directory {string} --
        _log_directory {string} -- Absolute path of the log subdirectory. It contains the logs of each execution of oftools_dsmigin.
        _working_directory {string} -- Absolute path of the working directory.

        _conversion {string} -- If the user specifies the conversion flag, it changes from '' to '-C' to perform conversion only migration type.
        _enable_column_list {list} --
        _encoding_code {string} -- It specifies to what ASCII characters the EBCDIC two-byte data should be converted.
        _force {string} -- If the user specifies the force flag, it changes from '' to '-F' to perform forced migration, which means erasing the dataset if already migrated in OpenFrame.
        _generations {integer} --
        _ip_address {string} -- The ip address of the mainframe to connect to for the Listcat and FTP executions.
        _listcat {Listcat object} --
        _prefix {string} --

        _tag {string} -- Keyword to tag ...

        _timestamp {Datetime} -- Date and time for ...

        _init_pwd {string} -- Absolute path of the initial directory where the command has been executed.

    Methods:
        __init__() -- Initializes all attributes of the class.
        clear_all() -- Clears context completely at the end of the program execution.
    """

    def __init__(self):
        """Initializes the class with all the attributes.
        """
        # Required variables for program execution
        self._init = False
        self._number = 0
        self._records = []

        # Directories
        self._conversion_directory = ''
        self._copybooks_directory = ''
        self._csv_backups_directory = ''
        self._datasets_directory = ''
        self._listcat_directory = ''
        self._log_directory = ''
        self._working_directory = ''

        # Input parameters - different jobs
        self._conversion = ''
        self._enable_column_list = []
        self._encoding_code = ''
        self._force = ''
        self._generations = 0
        self._ip_address = ''
        self._listcat = None
        self._prefix = ''
        self._test = False

        # Tag
        self._tag = ''

        # Timestamp
        self._time_stamp = datetime.datetime.now()

        # Other
        self._init_pwd = os.getcwd()

    @property
    def init(self):
        """Getter method for the attribute _init.

        Returns:
            boolean -- the value for _init.
        """
        return self._init

    @init.setter
    def init(self, init):
        """Setter method for the attribute _init.
        """
        if init is not None:
            self._init = init

    @property
    def number(self):
        """Getter method for the attribute _number.

        Returns:
            integer -- the value for _number.
        """
        return self._number

    @number.setter
    def number(self, number):
        """Setter method for the attribute _number.

        Raises:
            SystemError -- Exception is raised if number is negative.
        """
        try:
            if number is not None:
                if number > 0:
                    self._number = number
                else:
                    raise SystemError()
        except SystemError:
            option = '-n, --number'
            Log().logger.critical(ErrorM.SIGN.value % (option, number))
            sys.exit(-1)

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
    def working_directory(self, path):
        """Setter method for the attribute _working_directory and all its subdirectories.

        Only if the input work directory has been correctly specified, it creates the absolute path to this directory. It also creates the working directory if it does not exist already.
        
        Raises:
            FileNotFoundError -- Exception is raised if the working directory as well as the log (sub)directory do not exist.
        """
        working_directory = os.path.expandvars(path)

        self._working_directory = os.path.abspath(working_directory)
        self._conversion_directory = self._working_directory + '/conversion'
        self._copybooks_directory = self._working_directory + '/copybooks'
        self._csv_backups_directory = self._working_directory + '/csv_backups'
        self._datasets_directory = self._working_directory + '/datasets'
        self._listcat_directory = self._working_directory + '/listcat'
        self._log_directory = self._working_directory + '/log'

        if self._initialization:
            Log().logger.info(LogM.INIT_WORKING_DIR.value)

            FileHandler().create_directory(self._working_directory)
            FileHandler().create_directory(self._conversion_directory)
            FileHandler().create_directory(self._copybooks_directory)
            FileHandler().create_directory(self._csv_backups_directory)
            FileHandler().create_directory(self._datasets_directory)
            FileHandler().create_directory(self._listcat_directory)
            FileHandler().create_directory(self._log_directory)

        try:
            if FileHandler().is_a_directory(
                    self._working_directory) is False or FileHandler(
                    ).is_a_directory(self._log_directory) is False:
                raise FileNotFoundError()
            else:
                Log().logger.debug(LogM.WORKING_DIR_OK.value)
        except FileNotFoundError:
            Log().logger.critical(ErrorM.WORKING_DIR.value % path)
            Log().logger.critical(ErrorM.INIT.value % 'working directory')
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

        It checks if the format of the input IP address is correct. This method is able to detect both IPv4 and IPv6 addresses. It is a really simple pattern analysis.

        Arguments:
            ip_address {string} -- IP address used as as a parameter.

        Raises:
            SystemError -- Exception raised if the IP address specified does not respect a correct IPv4 or IPv6 format.
        """
        try:
            if ip_address is not None:
                # Analyze if the argument ip_address respect a valid format
                is_valid_ip = False

                # IPv4 pattern detection
                if ip_address.count('.') == 3:
                    fields = ip_address.split('.')
                    is_IPv4 = False
                    for field in fields:
                        if str(int(field)) == field and 0 <= int(field) <= 255:
                            is_IPv4 = True
                        else:
                            is_IPv4 = False
                            break
                    is_valid_ip = is_IPv4
                # IPv6 pattern detection
                if ip_address.count(':') == 7:
                    fields = ip_address.split(':')
                    is_IPv6 = False
                    for field in fields:
                        if len(field) > 4:
                            is_IPv6 = False
                            break
                        if int(field, 16) >= 0 and field[0] != '-':
                            is_IPv6 = True
                        else:
                            is_IPv6 = False
                            break
                    is_valid_ip = is_IPv6

                if is_valid_ip is True:
                    Log().logger.debug(LogM.IP_ADDRESS_OK.value)
                    self._ip_address = ip_address
                else:
                    raise SystemError()
        except SystemError:
            Log().logger.critical(ErrorM.IP.value % ip_address)
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
                Log().logger.warning(LogM.VSAM_LISTCAT_SKIP.value)
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
            option = '-g, --generations'
            Log().logger.critical(ErrorM.SIGN.value % (option, generations))
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
        if force is True:
            self._force = ' -F '

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
        if tag is None:
            self._tag, _, _ = ShellHandler().execute_command('logname')
            self._tag = '_' + self._tag.replace('\n', '')
        else:
            self._tag = '_' + tag

    @property
    def time_stamp(self, value='default'):
        """Getter method for the attribute _time_stamp.

        Arguments:
            value {string} -- Type of timestamp requested.

        Returns:
            string -- the value for _time_stamp.
        """
        if value == 'full':
            return self._time_stamp.strftime('%Y%m%d_%H%M%S')
        else:
            return self._time_stamp.strftime('%Y-%m-%d')

    def clear_all(self):
        """Clears context completely at the end of the program execution.
        """
        os.chdir(self._init_pwd)
