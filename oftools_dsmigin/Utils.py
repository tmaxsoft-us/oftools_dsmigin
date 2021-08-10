#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set of functions useful in any module.

    This module gathers a set of functions that are useful in many other modules. When a 
    function is widely used in different modules, a general version of it is created and 
    can be found here.

    Typical usage example:
      shell_result = Utils().execute_shell_command(shell_command)
      ftp_result = Utils().execute_ftp_command(ftp_command)"""

# Generic/Built-in modules
import csv
import os
import shutil
import subprocess
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


class Utils(object, metaclass=SingletonMeta):
    """A class used to run several useful functions.

        Attributes:
            _ip_address: A string, the ip address of the mainframe to connect to for the FTP execution.

        Methods:
            analyze_ip_address(ip_address): Checking the format of the ip address used as a parameter.
            check_command(shell_command): Check if the command exist in the environment using which.
            execute_shell_command(shell_command): Separate method to execute shell command.
            execute_ftp_command(ftp_command): Separate method to execute FTP command."""

    def analyze_ip_address(self, ip_address):
        """Checking the format of the ip address used as a parameter.

            This method is able to detect both IPv4 and IPv6 addresses. It is a really simple pattern analysis.

            Args:
                ip_address: A string, the ip address used as as a parameter.

            Returns:
                A boolean, if the ip address used as input is a fully qualified ip address or not."""
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

        if is_valid_ip:
            self._ip_address = ip_address

        return is_valid_ip

    def check_command(self, shell_command):
        """Check if the command exist in the environment using which.

            Returns:
                A boolean, True if the command does not exist and False if the command exist."""
        if shutil.which(shell_command) is None:
            return False
        else:
            return True

    def check_file_extension(self, file_path, file_extension):
        """
        """
        try:
            file_path_expand = os.path.expandvars(file_path)
            extension = file_path_expand.rsplit('.', 1)[1]

            if extension == file_extension:
                is_valid_ext = True
            else:
                is_valid_ext = False

        except IndexError:
            Log().logger.critical('IndexError: Given file does not have a .' +
                                  file_extension + ' extension: ' + file_path)
            sys.exit(-1)
        else:
            return is_valid_ext

    def copy_file(self, file_path_src, file_path_dst):
        """Copy a source file to its given destination.
            """
        try:
            shutil.copy(file_path_src, file_path_dst)
            #TODO Test copy to a folder that does not exist
            rc = 0
        except shutil.SameFileError as e:
            Log().logger.error('Failed to copy: %s' % e)
            rc = -1
        except OSError as e:
            Log().logger.error('Failed to copy: %s' % e)
            rc = -1

        return rc

    def create_directory(self, directory):
        """Creates the given directory if it does not already exists.
            """
        try:
            if os.path.isdir(directory) is False:
                Log().logger.debug(
                    'Directory does not exist: Creating new directory: ' +
                    directory)
                os.mkdir(directory)
            rc = 0
        except PermissionError:
            Log().logger.error(
                'PermissionError: Permission denied: Directory creation failed: '
                + directory)
            rc = -1

        return rc

    def execute_shell_command(self, shell_command):
        """Separate method to execute shell command.
            
            This method is dedicated to execute a shell command and it handles exceptions in case of 
            failure.

            Args:
                shell_command: A string, the actual shell command that needs to be executed.

            Returns:
                A tuple, which is the stdout, stderr, and return code of the shell command.

            Raises:
                UnicodeDecodeError: An error occurred if decoding the shell command result failed 
                    with utf-8. Use latin-1 instead."""
        #TODO Define default values for stdout, stderr, return_code
        root_command = shell_command.split()[0]
        command_exist = self.check_command(root_command)

        if command_exist:
            try:
                proc = subprocess.run(shell_command,
                                      shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
                stdout = proc.stdout.decode('utf_8')
                stderr = proc.stderr.decode('utf_8')
                return_code = proc.returncode
            except UnicodeDecodeError:
                stdout = proc.stdout.decode('latin_1')
                stderr = proc.stderr.decode('latin_1')
                return_code = proc.returncode
            except:
                stdout = None
                stderr = None
                return_code = -1
                return stdout,stderr, return_code

            if Log().level == 'DEBUG':
                if return_code != 0:
                    Log().logger.error(stdout)
                    Log().logger.error(stderr)
                    Log().logger.error('return code: ' + str(return_code))
                else:
                    Log().logger.debug(stdout)
                    Log().logger.debug(stderr)
                    Log().logger.debug('return code: ' + str(return_code))
            elif return_code != 0 :
                Log().logger.error(stdout)
                Log().logger.error(stderr)
        else:
            Log().logger.error('Command does not exist:' + root_command)

        return stdout, stderr, return_code

    def execute_ftp_command(self, ftp_command):
        """Separate method to execute FTP command.

            This method is dedicated to execute a ftp command and it handles exception in case of failure. The credentials to open the FTP session are provided through the file .netrc in the home directory. This configuration file needs to be created before the first execution of the tool."""
        # ! We might need to use sftp (FTP over SSH) with more security
        # ! By default, connection refused on port 22. After modification of
        # ! the PROFILE to add TCP connection on port 22, still not working
        connect_command = 'ftp ' + self._ip_address + '<< EOF\n binary\ncd ..\n'
        shell_command = connect_command + ftp_command

        return self.execute_shell_command(shell_command)

    def format_command(self, shell_command):
        """Prevent bugs in dsmigin execution by escaping some special characters.

            It currently supports escaping the following characters:
                - $
                - #

            Args:
                shell_command: A string, the input shell command that needs to be formatted.

            Returns:
                A string, the shell command correctly formatted ready for execution."""
        shell_command = shell_command.replace('$', '\\$')
        shell_command = shell_command.replace('#', '\\#')
        Log().logger.info(shell_command)

        return shell_command

    def read_file(self, file_path):
        """Open and read the input file.

            Supports following extensions:
                - configuration: conf, cfg, prof
                - text: log, tip, txt

            Args:
                path_to_file: A string, absolute path to the file.

            Returns: 
                A parsed file, the type depends on the extension of the processed file.

            Raises:
                FileNotFoundError: An error occurs if the file does not exist or is not found.
                IsADirectoryError: An error occurs if a directory is specified instead of a file.
                PermissionError: An error occurs if the user running the program does not have the required 
                    permissions to access the input file.
                SystemExit: An error occurs of the file is empty.
                TypeError: An error occurs if the file extension is not supported.

                MissingSectionHeaderError: An error occurs if the config file specified does not contain 
                    any section.
                DuplicateSectionError: An error occurs if there are two sections with the same name in the 
                    config file specified.
                DuplicateOptionError: An error occurs if there is a duplicate option in one of the sections 
                    of the config file specified."""
        try:
            file_path = os.path.expandvars(file_path)
            # Check on file size
            if os.stat(file_path).st_size <= 0:
                raise SystemError()

            if os.path.isfile(file_path):
                with open(file_path, mode='r') as fd:
                    extension = file_path.rsplit('.', 1)[1]

                    if extension == 'csv':
                        out = csv.reader(fd, delimiter=',')
                        file_data = []
                        for row in out:
                            file_data.append(row)
                    else:
                        raise TypeError()

            elif os.path.isdir(file_path):
                raise IsADirectoryError()
            else:
                raise FileNotFoundError()

        except FileNotFoundError:
            Log().logger.critical(
                'FileNotFoundError: No such file or directory: ' + file_path)
            sys.exit(-1)
        except IsADirectoryError:
            Log().logger.critical('IsADirectoryError: Is a directory: ' +
                                  file_path)
            sys.exit(-1)
        except IndexError:
            Log().logger.critical(
                'IndexError: Given file does not have an extension: ' +
                file_path)
            sys.exit(-1)
        except PermissionError:
            Log().logger.critical('PermissionError: Permission denied: ' +
                                  file_path)
            sys.exit(-1)
        except SystemError:
            Log().logger.critical('EmptyError: File empty: ' + file_path)
            sys.exit(-1)
        except TypeError:
            Log().logger.critical('TypeError: Unsupported file extension: ' +
                                  file_path)
            sys.exit(-1)
        else:
            return file_data