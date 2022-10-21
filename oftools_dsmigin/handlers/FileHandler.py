#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set of shared methods for any other module.

This module gathers a set of methods that are useful in many other modules.
When a method is widely used in different modules, a general version of it is
created and can be found here.

Typical usage example:
  FileHandler().read_file(path)
"""

# Generic/Built-in modules
import configparser
import collections
import csv
import json
import os
import shutil
import sys
import xml

# Third-party modules
import untangle

# Owned modules
from ..enums.Message import ErrorM, LogM
from ..Log import Log


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


class FileHandler(metaclass=SingletonMeta):
    """Run file and directories related tasks across all modules.

    Attributes:
        _config_extensions {list[string]} -- List of supported extensions for
            configuration files.
        _text_extensions {list[string]} -- List of supported extensions for
            text files.

    Methods:
        read_file(path) -- Opens and reads a file.
        write_file(path, content, mode) -- Writes content to the file.
        copy_file(src, dst) -- Copies the source file to its given destination.
        delete_file(path) -- Deletes the file.
        check_extension(path, extension) -- Checks of the given file has the
            correct extension.
        get_file_size(path) -- Evaluates the size of the file.
        get_file_md5_checksum (path) -- Evaluates the MD5 checksum of the input
            file.

        create_directory(path) -- Creates the given directory if it does not
            already exists.
        move_directory (src, dst) -- Moves the source directory to its given
            destination.
        delete_directory(path) -- Deletes an entire directory tree, whether it
            is empty or not.
        empty_directory(path) -- Removes all files and subdirectories from a
            given directory.
        is_a_directory(path) -- Evaluates if the given path is a directory or
            not.

        check_path_exists(path) -- Evaluates if the given path exists or not.
        check_write_access (path) -- Evaluates if the user has write access on
            the given path.
        get_files (path) -- Gets the list of files in a given path.
        get_duplicates(path, pattern) -- Gets duplicate files and folders in
            given path.
        get_creation_times(path) -- Gets creation time of the input path(s).
    """

    def __init__(self):
        """Initialize class attributes.
        """
        self._config_extensions = ["cfg", "conf", "ini", "prof", "toml"]
        self._text_extensions = ["log", "tip", "txt"]

    # File related methods

    def read_file(self, path):
        """Opens and reads the file.

        It saves the file's content in a variable.

        Arguments:
            path {string} -- Absolute path of the file.

        Returns:
            Parsed file, the type depends on the extension of the processed
            file.

        Raises:
            SystemError -- Exception raised if the file is empty.
            IsADirectoryError -- Exception raised if a directory is specified
                instead of a file.
            FileNotFoundError -- Exception raised if the file does not exist or
                is not found.
            PermissionError -- Exception raised if the user does not have the
                required permissions to read the file.
            IndexError -- Exception raised if the file extension is not found.
            TypeError --  Exception raised if the file extension is not
                supported.
            OSError -- Exception raised if an error didn't already raised one
                of the previous exceptions.

            MissingSectionHeaderError -- Exception raised if there is no
                section in the config file specified.
            DuplicateSectionError -- Exception raised if there are two sections
                with the same name in the config file specified.
            DuplicateOptionError -- Exception raised if there is a duplicate
                option in one of the sections of the config file specified.

            JSONDecodeError -- Exception raised if there is an error decoding
                the JSON file specified.
            ValueError -- Exception raised if the first argument is None /
                empty string.
            AttributeError -- Exception raised if a requested xml.sax feature
                is not found in xml.sax.handler.
            xml.sax.SAXParseException -- Exception raised if something goes
                wrong during parsing.
        """
        extension = ""
        file_data = None
        path_expand = os.path.expandvars(path)

        try:
            if os.path.isfile(path_expand):
                # Check on file size
                if os.path.getsize(path_expand) <= 0:
                    raise SystemError()

                with open(path_expand, mode="r", encoding="utf-8") as file:
                    extension = path_expand.rsplit(".", 1)[1]

                    if extension in self._config_extensions:
                        file_data = configparser.ConfigParser(
                            dict_type=collections.OrderedDict)
                        file_data.optionxform=str
                        file_data.read(path_expand)
                    elif extension == "csv":
                        out = csv.reader(file, delimiter=",")
                        file_data = []
                        for row in out:
                            file_data.append(row)
                    elif extension == "json":
                        file_data = json.load(file)
                    elif extension in self._text_extensions:
                        file_data = file.read()
                    elif extension == "xml":
                        file_data = untangle.parse(path_expand)
                    else:
                        raise TypeError()
            elif os.path.isdir(path_expand):
                raise IsADirectoryError()
            else:
                raise FileNotFoundError()

        except IsADirectoryError:
            Log().logger.critical(ErrorM.IS_A_DIR.value % path)
            sys.exit(-1)
        except FileNotFoundError:
            Log().logger.critical(ErrorM.FILE_NOT_FOUND.value % path)
            file_data = None
        except SystemError:
            Log().logger.critical(ErrorM.SYSTEM_EMPTY.value % path)
            sys.exit(-1)
        except PermissionError:
            Log().logger.critical(ErrorM.PERMISSION.value % path)
            sys.exit(-1)
        except IndexError:
            Log().logger.critical(ErrorM.INDEX_EXTENSION.value % path)
            sys.exit(-1)
        except TypeError:
            Log().logger.critical(ErrorM.TYPE_EXTENSION.value %
                                  (extension, path_expand))
            sys.exit(-1)
        except OSError as error:
            Log().logger.critical(ErrorM.OS_READ.value % error)
            sys.exit(-1)
        # configparser module related exceptions
        except configparser.MissingSectionHeaderError as error:
            Log().logger.critical(ErrorM.MISSING_SECTION_HEADER.value % error)
            sys.exit(-1)
        except configparser.DuplicateSectionError as error:
            Log().logger.critical(ErrorM.DUPLICATE_SECTION.value % error)
            sys.exit(-1)
        except configparser.DuplicateOptionError as error:
            Log().logger.critical(ErrorM.DUPLICATE_OPTION.value % error)
            sys.exit(-1)
        # json module related exceptions
        except json.JSONDecodeError as error:
            Log().logger.critical(ErrorM.JSON_DECODE.value % error)
            sys.exit(-1)
        # untangle related exceptions
        except ValueError as error:
            Log().logger.critical(ErrorM.VALUE.value % error)
            sys.exit(-1)
        except AttributeError as error:
            Log().logger.critical(ErrorM.ATTRIBUTE.value % error)
            sys.exit(-1)
        except xml.sax.SAXParseException as error:
            Log().logger.critical(ErrorM.XML_SAX_PARSE.value % error)
            sys.exit(-1)

        return file_data

    def write_file(self, path, content, mode="w"):
        """Writes content to the file.

        Arguments:
            path {string} -- Absolute path of the file.
            content {string or list[string]} -- Content that needs to be
                written to the file.
            mode {string} -- Mode used to write the file. Most common values:
                "a" or "w".

        Returns:
            integer -- Return code of the method.

        Raises:
            IsADirectoryError -- Exception raised if a directory is specified
                instead of a file.
            PermissionError -- Exception raised if  the user does not have the
                required permissions to write to the file.
            IndexError -- Exception raised if the file extension is not found.
            TypeError -- Exception raised if the file extension is not
                supported.
        """
        extension = ""
        path_expand = os.path.expandvars(path)

        try:
            if os.path.isdir(path_expand) is False:

                with open(path_expand, mode, encoding="utf-8") as file:
                    extension = path_expand.rsplit(".", 1)[1]

                    if extension in self._config_extensions:
                        content.write(file)
                    elif extension == "csv":
                        if isinstance(content, collections.OrderedDict):
                            writer = csv.DictWriter(file, delimiter=",")
                            writer.writerows(content)
                        else:
                            writer = csv.writer(file, delimiter=",")
                            if isinstance(content, str):
                                writer.writerow(content)
                            elif isinstance(content, list):
                                writer.writerows(content)
                    elif extension == "json":
                        json.dump(content, file)
                    elif extension in self._text_extensions:
                        if isinstance(content, str):
                            file.write(content)
                        elif isinstance(content, list):
                            for line in content:
                                file.write(line)
                    else:
                        raise TypeError()
                status = 0
            else:
                raise IsADirectoryError()

        except IsADirectoryError:
            Log().logger.critical(ErrorM.IS_A_DIR.value % path)
            status = -1
        except PermissionError:
            Log().logger.critical(ErrorM.PERMISSION.value % path)
            status = -1
        except IndexError:
            Log().logger.critical(ErrorM.INDEX_EXTENSION.value % path)
            status = -1
        except TypeError:
            Log().logger.critical(ErrorM.TYPE_EXTENSION.value %
                                  (extension, path_expand))
            status = -1

        return status

    @staticmethod
    def copy_file(src, dst):
        """Copy the source file to the destination file.

        Arguments:
            src {string} -- Absolute path of the source file.
            dst {string} -- Absolute path of the destination file.

        Returns:
            integer -- Return code of the method.

        Raises:
            shutil.SameFileError -- Exception raised if the file already exist.
            OSError -- Exception raised if an error didn't already raised one
                of the previous exceptions.
        """
        src_expand = os.path.expandvars(src)
        dst_expand = os.path.expandvars(dst)

        try:
            shutil.copy(src_expand, dst_expand)
            Log().logger.debug(LogM.CP_SUCCESS.value % (src, dst))
            status = 0
        except shutil.SameFileError:
            Log().logger.debug(ErrorM.SHUTIL_SAME_FILE.value % (src, dst))
            status = 0
        except OSError as error:
            Log().logger.critical(ErrorM.OS_COPY.value % error)
            status = -1

        return status

    @staticmethod
    def check_extension(path, ext_reference):
        """Checks if the file has the correct extension.

        Arguments:
            path {string} -- Absolute path of the file.
            extension {string} -- File extension that needs to match.

        Returns:
            boolean -- True if the file extension is correct and False
                otherwise.

        Raises:
            IndexError -- Exception raised if the given file has an incorrect
                extension.
            TypeError -- Exception raised if the extension does not match.
        """
        extension = ""
        path_expand = os.path.expandvars(path)

        try:
            extension = path_expand.rsplit(".", 1)[1]
            if extension == ext_reference:
                is_valid_ext = True
            else:
                raise TypeError()
        except IndexError:
            Log().logger.critical(ErrorM.INDEX_EXTENSION.value %
                                  (ext_reference, path))
            Log().logger.critical(ErrorM.ABORT.value)
            sys.exit(-1)
        except TypeError:
            Log().logger.error(ErrorM.TYPE_EXTENSION.value %
                               (extension, path_expand))
            is_valid_ext = False

        return is_valid_ext

    # Directory related methods

    @staticmethod
    def create_directory(path, type_dir=""):
        """Creates the given directory if it does not already exists.

        Arguments:
            path {string} -- Absolute path of the directory.

        Returns:
            integer -- Return code of the method.

        Raises:
            FileExistsError -- Exception raised if the directory already exists.
            OSError -- Exception raised if an error didn't already raised one
                of the previous exceptions.
        """
        path_expand = os.path.expandvars(path)

        try:
            # Check if the directory already exists
            if os.path.isdir(path_expand) is False:
                Log().logger.debug(LogM.DIR_NOT_EXIST.value % path)
                os.mkdir(path_expand)

                Log().logger.debug(LogM.DIR_CREATED.value % path)
                status = 0
            else:
                raise FileExistsError()
        except FileExistsError:
            if type_dir == "po":
                Log().logger.debug(ErrorM.FILE_EXISTS.value % path)
                status = 1
            else:
                status = 0
        except OSError as error:
            Log().logger.critical(ErrorM.OS_DIRECTORY_CREATION.value % error)
            sys.exit(-1)

        return status

    @staticmethod
    def empty_directory(path):
        """Removes all files and subdirectories from a given directory.

        Arguments:
            path {string} -- Absolute path of the directory.

        Returns:
            integer -- Return code of the method.

        Raises:
            FileNotFoundError -- Exception raised if the directory does not
                exist or is not found.
            NotADirectoryError -- Exception raised if the path is not a
                directory.
            PermissionError -- Exception raised if the user does not have the
                required permissions to delete the directory's content.
            OSError -- Exception raised if an error didn't already raised one
                of the previous exceptions.
        """
        path_expand = os.path.expandvars(path)

        try:
            if os.path.exists(path_expand):
                # Check if directory is empty
                if os.path.isdir(path_expand):
                    if len(os.listdir(path_expand)) == 0:
                        Log().logger.debug(LogM.DIR_EMPTY.value % path)
                    else:
                        for element in os.scandir(path_expand):
                            shutil.rmtree(element, ignore_errors=False)
                        Log().logger.debug(LogM.DIR_PROCESS_EMPTY.value % path)
                    status = 0
                else:
                    raise NotADirectoryError()
            else:
                raise FileNotFoundError()

        except FileNotFoundError:
            Log().logger.critical(ErrorM.FILE_NOT_FOUND.value % path)
            sys.exit(-1)
        except NotADirectoryError:
            Log().logger.critical(ErrorM.NOT_A_DIR.value % path)
            sys.exit(-1)
        except PermissionError:
            Log().logger.critical(ErrorM.PERMISSION.value % path)
            sys.exit(-1)
        except OSError as error:
            Log().logger.critical(ErrorM.OS_DELETE.value % error)
            sys.exit(-1)
        else:
            return status

    @staticmethod
    def is_a_directory(path):
        """Evaluates if the given path is a directory or not.

        Arguments:
            path {string} -- Absolute path of the directory.

        Returns:
            boolean -- True if the path is a directory, False otherwise.

        Raises:
            NotADirectoryError -- Exception raised if the path is not a
                directory.
        """
        path_expand = os.path.expandvars(path)

        try:
            if os.path.isdir(path_expand):
                is_a_directory = True
            else:
                raise NotADirectoryError()
        except NotADirectoryError:
            Log().logger.critical(ErrorM.NOT_A_DIR.value % path)
            is_a_directory = False

        return is_a_directory

    # Other

    @staticmethod
    def check_path_exists(path):
        """Evaluates if the given path exists or not.

        Arguments:
            path {string} -- Absolute path of the file or directory.

        Returns:
            boolean -- True of the path exists, False otherwise.
        """
        path_expand = os.path.expandvars(path)
        return os.path.exists(path_expand)

    @staticmethod
    def get_files(path):
        """Gets the list of files in the path.

        Arguments:
            path {string} -- Absolute path of the file or directory.

        Returns:
            list[string] -- List of file absolute paths.

        Raises:
            FileNotFoundError -- Exception raised if the path does not exist or
                is not found.
        """
        path_expand = os.path.expandvars(path)

        try:
            if os.path.isfile(path_expand):
                file_paths = [os.path.abspath(path_expand)]

            elif os.path.isdir(path_expand):
                file_paths = [
                    os.path.abspath(os.path.join(root, filename))
                    for root, _, files in os.walk(path_expand)
                    for filename in files
                    if not filename.startswith(".")
                ]
                # Sort the list alphabetically
                file_paths.sort()
            else:
                raise FileNotFoundError()
        except FileNotFoundError:
            Log().logger.critical(ErrorM.FILE_NOT_FOUND.value % path)
            sys.exit(-1)

        return file_paths
