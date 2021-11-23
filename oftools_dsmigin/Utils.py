#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set of functions useful in any module.

    This module gathers a set of functions that are useful in many other modules. When a 
    function is widely used in different modules, a general version of it is created and 
    can be found here.

    Typical usage example:
        shell_result = Utils().execute_shell_command(shell_command)
        ftp_result = Utils().execute_ftp_command(ftp_command)
    """

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
            _ip_address {string} -- The ip address of the mainframe to connect to for the FTP execution.

        Methods:
            analyze_ip_address(ip_address) -- Checks the format of the given ip address.
            check_command(shell_command) -- Checks if the command exist in the environment using which.
            check_file_extension(file_path, file_extension) -- Checks of the given file has the correct extension.
            copy_file(file_path_src, file_path_dst) -- Copy a source file to its given destination.
            create_directory(directory) -- Creates the given directory if it does not already exists.
            execute_shell_command(shell_command) -- Dedicated method to execute a shell command.
            execute_ftp_command(ftp_command) -- Dedicated method to execute an FTP command.
            format_command(shell_command) -- Prevents bugs in dsmigin execution by escaping some special characters.
            read_file(file_path) -- Opens and reads the input file.
        """

    def analyze_ip_address(self, ip_address):
        """Checks the format of the given ip address.

            This method is able to detect both IPv4 and IPv6 addresses. It is a really simple pattern analysis.

            Arguments:
                ip_address {string} -- the ip address used as as a parameter.

            Returns:
                boolean -- If the ip address used as input is a fully qualified ip address or not.
            """
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
        """Checks if the command exist in the environment using which.

            Arguments:
                shell_command {string} -- The shell command that needs to be tested.

            Returns:
                boolean -- True if the command does not exist and False if the command exist.
            """
        if shutil.which(shell_command) is None:
            return False
        else:
            return True

    def check_file_extension(self, file_path, file_extension):
        """Checks of the given file has the correct extension.

            Arguments:
                file_path {string} -- Absolute path to the file.
                file_extension {string} -- File extension that needs to match.

            Returns:
                boolean -- True if the file extension is correct and False otherwise.
            
            Raises:
                IndexError -- Exception is raised if the given file has an incorrect extension.
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

            Arguments:
                file_path_src {string} -- Absolute path to the source file.
                file_path_dst {string} -- Absolute path to the destination file.

            Returns:
                integer -- Return code of the method.
            
            Raises:
                shutil.SameFileError -- Exception is raised if the file already exist.
                OSError -- Exception is raised if there is an issue related to the system while copying.
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

            Arguments:
                directory {string} -- Absolute path to the directory.

            Returns:
                integer -- Return code of the method.
            
            Raises:
                PermissionError -- Exception is raised if there is a permission issue during folder creation.
            """
        try:
            if os.path.isdir(directory) is False:
                Log().logger.debug(
                    'Directory does not exist: Creating new directory: ' +
                    directory)
                os.mkdir(directory)
            rc = 0
        except PermissionError:
            Log().logger.critical(
                'PermissionError: Permission denied: Directory creation failed: '
                + directory)
            sys.exit(-1)
        else:
            return rc

    def execute_shell_command(self, shell_command):
        """Dedicated method to execute a shell command.
            
            This method is dedicated to execute a shell command and it handles exceptions in case of 
            failure.

            Arguments:
                shell_command {string} -- The shell command that needs to be executed.

            Returns:
                tuple -- The tuple elements are stdout, stderr, and return code of the shell command.

            Raises:
                UnicodeDecodeError -- Exception is raised if decoding the shell command result failed 
                    with utf-8. latin-1 is used instead.
            """
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
            except KeyboardInterrupt:
                raise KeyboardInterrupt()
            except:
                stdout = None
                stderr = None
                return_code = -1
                return stdout, stderr, return_code

            if Log().level == 'DEBUG':
                if return_code != 0:
                    Log().logger.error(stdout)
                    Log().logger.error(stderr)
                    Log().logger.error('return code: ' + str(return_code))
                else:
                    Log().logger.debug(stdout)
                    Log().logger.debug(stderr)
                    Log().logger.debug('return code: ' + str(return_code))
            elif return_code != 0:
                Log().logger.error(stdout)
                Log().logger.error(stderr)
        else:
            Log().logger.error('Command does not exist:' + root_command)

        return stdout, stderr, return_code

    def execute_ftp_command(self, ftp_command):
        """Dedicated method to execute an FTP command.

            This method is dedicated to execute a ftp command and it handles exception in case of failure. The credentials to open the FTP session are provided through the file .netrc in the home directory. This configuration file needs to be created before the first execution of the tool.

            Arguments:
                ftp_command {string} -- The FTP command that needs to be executed.

            Returns:
                string - the result of the FTP command.
            """
        # ! We might need to use sftp (FTP over SSH) with more security
        # ! By default, connection refused on port 22. After modification of
        # ! the PROFILE to add TCP connection on port 22, still not working
        connect_command = 'ftp ' + self._ip_address + '<< EOF\n binary\ncd ..\n'
        quit_command = '\nquit\nEOF'

        shell_command = connect_command + ftp_command + quit_command
        stdout, stderr, return_code = self.execute_shell_command(shell_command)

        if return_code == 0:
            if 'not found' in stdout or 'No data sets found.' in stdout or 'cannot be processed' in stdout:
                return_code = -1

        return stdout, stderr, return_code

    def format_command(self, shell_command):
        """Prevents bugs in dsmigin execution by escaping some special characters.

            It currently supports escaping the following characters:
                - $
                - #

            Arguments:
                shell_command {string} -- The shell command that needs to be formatted.

            Returns:
                string -- The shell command correctly formatted ready for execution.
            """
        shell_command = shell_command.replace('$', '\\$')
        shell_command = shell_command.replace('#', '\\#')
        Log().logger.info(shell_command)

        return shell_command

    def read_file(self, file_path):
        """Opens and reads the input file.

            Supports following extensions:
                - configuration: conf, cfg, prof
                - text: log, tip, txt

            Arguments:
                path_to_file: A string, absolute path to the file.

            Returns: 
                Parsed file -- the type depends on the extension of the processed file.

            Raises:
                FileNotFoundError -- Exception is raised if the file does not exist or is not found.
                IsADirectoryError -- Exception is raised if a directory is specified instead of a file.
                PermissionError -- Exception is raised if the user running the program does not have the required 
                    permissions to access the input file.
                SystemExit -- Exception is raised if the file is empty.
                TypeError -- Exception is raised if the file extension is not supported.

                MissingSectionHeaderError -- Exception is raised if the config file specified does not contain 
                    any section.
                DuplicateSectionError -- Exception is raised if there are two sections with the same name in the 
                    config file specified.
                DuplicateOptionError -- Exception is raised if there is a duplicate option in one of the sections 
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
                    elif extension == 'txt':
                        file_data = fd.read()
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