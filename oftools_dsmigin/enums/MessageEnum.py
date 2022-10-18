#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enumeration module for error and log messages.
"""

# Generic/Built-in modules
import enum

# Third-party modules

# Owned modules


@enum.unique
class Color(enum.Enum):
    """A class used to list all colors used in this program.
    """
    GREEN = '\x1b[92m'
    RED = '\x1b[91m'
    WHITE = '\x1b[39m'


@enum.unique
class ErrorM(enum.Enum):
    """A class used to list all error messages used in this program.
    """

    # Shared
    ABORT = 'Error: Aborting program execution'
    INIT = 'Please initialize the %s with the --init CLI option'
    LISTCAT_FTP = 'ListcatFTPError: No such dataset on Mainframe: %s'

    # Context module
    IP = 'IPAddressFormatError: -i, --ip-address option value must respect either IPv4 or IPv6 standard format: %s'
    SIGN = 'SignError: Invalid %s option: Must be positive: %d'
    WORKING_DIR = 'FileNotFoundError: No such dataset migration working directory: %s'

    # CSV module
    HEADERS_WARNING = 'HeadersWarning: Headers in the CSV file do not match the program definition: %s'
    INDEX_ELEMENTS_LINE = 'IndexError: Too many elements in the line number %d of the CSV file'

    # FTPJob module
    FTP_DOWNLOAD = 'FTPDownloadError: Cannot proceed with dataset: %s'

    # ListcatJob module

    # Main module
    ARGUMENT = 'ArgumentError: %s'
    JOB = 'JobError: Unexpected error detected during the job creation'
    KEYBOARD_INTERRUPT = 'KeyboardInterrupt: Execution ended by user'
    MISSING_IP_ERROR = 'MissingArgumentError: Missing -i, --ip-address option: Must be specified for dataset download from Mainframe'
    MISSING_IP_WARNING = 'MissingArgumentWarning: Missing -i, --ip-address option: Skipping dataset information retrieval from Mainframe'

    # Handlers

    # FileHandler module
    ATTRIBUTE = 'AttributeError: %s'
    DUPLICATE_OPTION = 'DuplicateOptionError: %s'
    DUPLICATE_SECTION = 'DuplicateSectionError: %s'
    FILE_EXISTS = 'FileExistsError: File or directory already exists: %s'
    FILE_NOT_FOUND = 'FileNotFoundError: No such file or directory: %s'
    INDEX_EXTENSION = 'IndexError: File extension %s not found: %s'
    IS_A_DIR = 'IsADirectoryError: Is a directory: %s'
    JSON_DECODE = 'JSONDecodeError: %s'
    MISSING_SECTION_HEADER = 'MissingSectionHeaderError: %s'
    NOT_A_DIR = 'NotADirectoryError: Is not a directory: %s'
    OS_COPY = 'OSError: Failed to copy: %s'
    OS_DELETE = 'OSError: Failed to delete directory: %s'
    OS_DIRECTORY_CREATION = 'OSError: Directory creation failed: %s'
    OS_READ = 'OSError: Failed to read the file: %s'
    PERMISSION = 'PermissionError: Permission denied: %s'
    SHUTIL_SAME_FILE = 'shutil.SameFileError: %s and %s are the same file'
    SYSTEM_EMPTY = 'EmptyError: File empty: %s'
    TYPE_EXTENSION = 'TypeError: Unsupported %s file extension: %s'
    VALUE = 'ValueError: %s'
    XML_SAX_PARSE = 'XML_SAXParseException: %s'

    # ShellHandler module
    CALLED_PROCESS = 'CalledProcessError: %s'
    SYSTEM_SHELL = 'ShellError: Command does not exist: %s'
    UNICODE = 'UnicodeDecodeError: Using latin-1 instead of utf-8 to decode stdout and stderr'


@enum.unique
class LogM(enum.Enum):
    """A class used to list all log messages used in this program.
    """

    # Shared
    COL_EMPTY = 'Missing parameter: %s column empty'
    COL_F = '[%s] %s column set to "F"'
    COL_INVALID = 'Invalid parameter: %s'
    COL_N = '%s column set to "N"'
    COL_NOT_SET = '%s column not set'
    COL_VALUE = '[%s] %s column set to "%s"'
    COL_Y = '%s column set to "Y"'
    COMMAND = '[%s] %s'
    DSORG_GDG = 'DSORG set to "GDG": Ignoring GDG base for %s'
    ELIGIBILITY = '[%s] Assessing dataset eligibility: %s'
    ELIGIBLE = '[%s] Proceeding, dataset eligible: %s'
    END_JOB = '[%s] Ending Job'
    FIELDS_EMPTY = '[%s] Fields empty'
    FIELDS_INCOMPLETE = '[%s] Fields incomplete'
    FTP_EMPTY = '[%s] FTP result empty'
    NOT_SUPPORTED = '[%s] Scenario not supported'
    SKIP_DATASET = '[%s] Skipping dataset: %s: '
    START_JOB = '[%s] Starting Job'

    # Context module
    INIT_WORKING_DIR = 'Initializing working directory'
    IP_ADDRESS_OK = 'Proper ip address specified: Proceeding'
    WORKING_DIR_OK = 'Proper dataset migration working directory specified: Proceeding'

    # CSV module
    CSV_BACKUP = ' (CSV) Backing up file: %s'
    CSV_INIT = '(CSV) Initializing file from template: %s'
    CSV_READ = '(CSV) Reading data from file: %s'
    CSV_WRITE = '(CSV) Writing data to file: %s'
    HEADERS_DSN_ONLY = '(CSV) List of dataset names only'
    HEADERS_FILE = '(CSV) Headers from input file: %s'
    HEADERS_FIX = '(CSV) Running headers auto-correct'
    HEADERS_OK = '(CSV) Headers correctly specified'
    HEADERS_PROG = '(CSV) Headers in program definition: %s'

    # DatasetRecord module
    FORMAT_RECORD = '(CSV) Formatting record due to some changes: Adding trailing spaces to record: %s'

    # FTPJob module
    DOWNLOAD = '[%s] Downloading dataset: %s'
    FTP_STATUS = 'FTP %s (%fs)' + Color.WHITE.value
    PREFIX_MISSING = 'Missing command line option -p, --prefix: Required for VSAM dataset download from Mainframe'
    PREFIX_OK = '[%s] Prefix correctly specified for VSAM dataset download'
    TAPE_FB = '[%s] Dataset downloaded from Tape: RECFM set to FB'
    TAPE_INCORRECT = '[%s] Dataset incorrectly downloaded: Run FTP again for the given dataset: %s'
    TAPE_VB = '[%s] Dataset downloaded from Tape: RECFM set to VB (FIXrecfm not found in command output)'
    VOLSER = 'VOLSER column set to "%s"'
    VOLSER_TAPE = '[%s] VOLSER set to "Tape": Downloading and retrieving dataset info'

    # GDG module
    GEN_FAIL = '[gdg] Generations found but all dataset info retrievals failed'
    GEN_FOR_BASE = '[gdg] Getting generations for the dataset: %s'
    GEN_MAX = '[gdg] Maximum number of generations reached'
    GEN_PROCESS = '[gdg] Current generation being processed: %s'
    GEN_SKIP = '[gdg] Skipping generation'
    LISTCAT_GDG_STATUS = 'LISTCAT GDG %s' + Color.WHITE.value
    LISTCAT_GDG_GEN = 'LISTCAT GDG GENERATION %s' + Color.WHITE.value
    NEW_RECORD = '[gdg] Adding new record for the generation: %s'
    NO_GEN = '[gdg] No generation found for the GDG base: %s'
    OLDEST_GEN = '[gdg] Oldest generation reached'
    PATTERN_NOT_SUPPORTED = '[gdg] Dataset name pattern not supported: %s'

    # Job module

    # Listcat module
    END_LISTCAT_GEN = '(LISTCAT) Ending CSV file generation'
    DATASET_IDENTIFIED = '(LISTCAT) Dataset identified: %s'
    LISTCAT_GEN_STATUS = 'LISTCAT FILE GENERATION %s' + Color.WHITE.value
    LISTCAT_READ = '(LISTCAT) Reading data from file: %s'
    LISTCAT_SKIP = '(LISTCAT) Skipping CSV file data retrieval for VSAM datasets: No such file or directory: %s'
    LISTCAT_WRITE = '(LISTCAT) Writing data to file: %s'
    START_LISTCAT_GEN = '(LISTCAT) Starting CSV file generation'

    # ListcatHandler module
    FTP_LS_AGAIN = '[%s] Running the FTP "ls" command once again'
    MIGRATED = '[%s] Dataset marked as "Migrated"'
    TAPE = '[%s] Dataset in "Tape" volume'

    # ListcatJob module
    DATASET_FOUND = '[%s] Dataset found in the listcat file: Updating migration record'
    DATASET_NOT_FOUND = '[%s] Dataset not found in the listcat file: Skipping dataset'
    LISTCAT_FILE_STATUS = 'LISTCAT FILE %s' + Color.WHITE.value
    LISTCAT_MAINFRAME_STATUS = 'LISTCAT MAINFRAME %s' + Color.WHITE.value
    LISTCAT_STATUS = 'LISTCAT %s (%fs)' + Color.WHITE.value
    REMOVE_DATASET = '[%s] Removing dataset from CSV file: This is not useful for the migration to OpenFrame: %s'

    # Main module
    COUNT = 'Current dataset count: %d'
    COUNT_MAX = 'Current dataset count: %d/%d'
    LIMIT = 'Limit of dataset processing reached'
    SKIP = 'Skipping dataset: rc = %d'
    TERMINATE = 'Terminating program execution'

    # MigrationJob module
    OF_LISTCAT_NOT_ENOUGH = '[%s] Not enough data in the listcat command output'
    OF_LISTCAT_NOT_WORKING = ' [%s] Listcat command not working correctly'
    MIGRATION_STATUS = 'MIGRATION %s (%fs)' + Color.WHITE.value
    SKIP_MIGRATION = '[%s] Dataset already exist in OpenFrame: Skipping migration'

    # Handlers

    # FileHandler module
    CP_SUCCESS = 'Successful copy of %s to %s'
    DIR_CREATED = 'Directory successfully created: %s'
    DIR_EMPTY = 'Directory empty: %s'
    DIR_NOT_EXIST = 'Directory does not exist: Creating new directory: %s'
    DIR_PROCESS_EMPTY = 'Directory successfully emptied: %s'

    # ShellHandler module
    CATALOG_COLUMN = '[migration] Using column value for CATALOG option: %s'
    CATALOG_DEFAULT = '[migration] Using default value for CATALOG option: SYS1.MASTER.ICFCAT'
    COPYBOOK_COLUMN = '[migration] Using column value for COPYBOOK option: %s'
    COPYBOOK_DEFAULT = '[migration] Using default value for COPYBOOK option: %s.conv'
    GET_GENERATIONS = '[gdg] Retrieving dataset generations from Mainframe: %s'
    GET_MAINFRAME = '[listcat] Retrieving dataset info from Mainframe: %s'
    RECALL = '[listcat] Recalling migrated dataset: %s'
    RETURN_CODE = 'Return code: %s'
    VOLSER_COLUMN = '[migration] Using column value for VOLSER option: %s'
    VOLSER_DEFAULT = '[migration] Using default value for VOLSER option: DEFVOL'
    VOLSER_SET_DEFAULT = '[migration] VOLSER set to: %s: Using default value instead: DEFVOL'
