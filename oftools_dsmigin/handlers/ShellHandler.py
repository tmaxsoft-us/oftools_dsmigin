#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set of methods useful in any module.

This module gathers a set of methods that are useful in many other modules. When a method is widely 
used in different modules, a general version of it is created and can be found here.

Typical usage example:
    ShellHandler().execute_command(command)
"""

# Generic/Built-in modules
import os
import shutil
import subprocess

# Third-party modules

# Owned modules
from ..enums.MessageEnum import ErrorM, LogM
from ..enums.MigrationEnum import MCol
from ..Log import Log


class SingletonMeta(type):
    """This pattern restricts the instantiation of a class to one object.
    
    It is a type of creational pattern and involves only one class to create methods and specified objects. It provides a global point of access to the instance created.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ShellHandler(metaclass=SingletonMeta):
    """A class used to run shell related tasks across all modules.

    Attributes:
        _env {dictionary} -- Environment variables for the execution of the program.

    Methods:
        _is_command_exist(command) -- Checks if the command exists in the environment using which.
        _run_command(command, env) -- Runs the command, using variables from the environment if any.
        _read_command(process) -- Decode stdout and stderr from the CompletedProcess object.
        _log_command(stdout, stderr, return_code, command_type) -- Log output and errors if any, with different log levels.
        execute_command(command, command_type, env=None) -- Executes shell command.

        recall(dataset_name, job_name, ip_address) -- Executes FTP command to make dataset available to download.

        execute_tbsql_command(tbsql_query) -- Separate method to execute a Tibero SQL query.
        execute_isql_command(isql_query) -- Separate method to execute an iSQL query.
        execute_sql_query(sql_query) -- Separate method to execute a SQL query using the pyodbc module.
        
        evaluate_filter(section, filter_name): Evaluates the status of the filter function passed as an argument.

        evaluate_env_variable(self, environment_variable) -- Evaluates if the input variable exists in the current environment.
    """

    def __init__(self):
        """Initializes all attributes of the class.
        """
        self._env = os.environ.copy()

    # Shell command related methods

    @staticmethod
    def _is_command_exist(command):
        """Checks if the command exists in the environment using which.

        Arguments:
            command {string} -- Shell command that needs to be checked.

        Returns:
            boolean -- True if the command does exist, and False otherwise.
        """
        return bool(shutil.which(command))

    @staticmethod
    def _format_command(command):
        """Prevents bugs in dsmigin execution by escaping some special characters.

        It currently supports escaping the following characters:
            - $
            - #

        Arguments:
            command {string} -- Shell command that needs to be formatted.

        Returns:
            string -- The shell command correctly formatted ready for execution.
        """
        command = command.replace('$', '\\$')
        command = command.replace('#', '\\#')

        return command

    @staticmethod
    def _run_command(command, env):
        """Runs the command, using variables from the environment if any.

        Arguments:
            command {string} -- Shell command that needs to be executed.
            env {dictionary} -- Environment variables currently in the shell environment.

        Returns:
            CompletedProcess object -- Object containing multiple information on the command execution.
        """
        process = subprocess.run(command,
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 check=False,
                                 env=env)
        return process

    @staticmethod
    def _read_command(process):
        """Decode stdout and stderr from the CompletedProcess object.

        Arguments:
            process {CompletedProcess object} -- Object containing multiple information on the command execution.

        Returns:
            tuple -- stdout, stderr, and return code of the shell command.

        Raises:
            UnicodeDecodeError -- Exception raised if there is an issue decoding a certain character in stdout or stderr.
        """
        try:
            stdout = process.stdout.decode('utf_8')
            stderr = process.stderr.decode('utf_8')
        except UnicodeDecodeError:
            Log().logger.debug(ErrorM.UNICODE.value)
            stdout = process.stdout.decode('latin_1')
            stderr = process.stderr.decode('latin_1')

        return_code = process.returncode

        return stdout, stderr, return_code

    @staticmethod
    def _log_command(stdout, stderr, return_code):
        """Log output and errors if any, with different log levels.

        Arguments:
            stdout {string} -- Standard output of the command.
            stderr {string} -- Standard error of the command.
            return_code {integer} -- Return code of the command.
            command_type {string} -- Type of the command to execute.
        """
        if return_code != 0:
            Log().logger.error(stdout)
            Log().logger.error(stderr)
            Log().logger.error(LogM.RETURN_CODE.value % return_code)

        elif Log().level == 'DEBUG':
            Log().logger.debug(stdout)
            Log().logger.debug(stderr)
            Log().logger.debug(LogM.RETURN_CODE.value % return_code)

    def execute_command(self, command, command_type='', env=None):
        """Executes shell command.
        
        This method is dedicated to execute a shell command and it handles exceptions in case of failure.

        Arguments:
            command {string} -- Shell command that needs to be executed.
            command_type {string} -- Type of the command to execute.
            env {dictionary} -- Environment variables currently in the shell environment.

        Returns:
            tuple -- stdout, stderr, and return code of the shell command.

        Raises:
            KeyboardInterrupt -- Exception raised if the user press Ctrl+C during the command shell execution.
            SystemError -- Exception raised if the command does not exist.
            subprocess.CalledProcessError -- Exception raised if an error didn't already raised one of the previous exceptions.
        """
        error = False

        if env is None:
            env = self._env

        try:
            command = os.path.expandvars(command)
            root_command = command.split()[0]

            if self._is_command_exist(root_command):
                if command_type == 'migration':
                    command = self._format_command(command)

                process = self._run_command(command, env)
                stdout, stderr, return_code = self._read_command(process)
            else:
                raise SystemError()
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except SystemError:
            Log().logger.error(ErrorM.SYSTEM_SHELL % root_command)
            error = True
        except subprocess.CalledProcessError as error:
            Log().logger.error(ErrorM.CALLED_PROCESS.value % error)
            error = True

        if error is True:
            stdout, stderr, return_code = None, None, -1

        self._log_command(stdout, stderr, return_code)

        return stdout, stderr, return_code

    def execute_ftp_command(self, ftp_command, ip_address):
        """Dedicated method to execute an FTP command.

        This method is dedicated to execute a ftp command and it handles exception in case of failure. The credentials to open the FTP session are provided through the file .netrc in the home directory. This configuration file needs to be created before the first execution of the tool.

        Arguments:
            ftp_command {string} -- The FTP command that needs to be executed.
            ip_address {string} --

        Returns:
            tuple -- stdout, stderr, and return code of the ftp command.
        """
        #TODO Investigate usage of SFTP (more secure)
        connect_command = 'ftp ' + ip_address + '<< EOF\n binary\ncd ..\n'
        quit_command = '\nquit\nEOF'

        shell_command = connect_command + ftp_command + quit_command
        stdout, stderr, return_code = self.execute_command(shell_command)

        if return_code == 0:
            if 'not found' in stdout or 'No data sets found.' in stdout or 'cannot be processed' in stdout:
                return_code = -1

        return stdout, stderr, return_code

    def ftp_ls(self, dataset_name, job_name, ip_address):
        """

        Arguments:
            dataset_name {string} -- Dataset name.
            job_name {string} -- Job name.
            ip_address {string} -- IP address of the Mainframe server.

        Returns:
            tuple -- stdout, stderr, and return code of the recall command.
        """
        Log().logger.info(LogM.GET_MAINFRAME.value % dataset_name)
        ftp_ls = 'ls ' + dataset_name

        Log().logger.debug(LogM.COMMAND.value % (job_name, ftp_ls))
        stdout, stderr, return_code = self.execute_ftp_command(
            ftp_ls, ip_address)

        return stdout, stderr, return_code

    def ftp_recall(self, dataset_name, job_name, ip_address):
        """Executes FTP command to make dataset available to download.

        If a dataset has VOLSER set to 'Migrated', the program executes this recall method just to open the directory containing the dataset to trigger download execution from the mainframe.

        Arguments:
            dataset_name {string} -- Dataset name.
            job_name {string} -- Job name.
            ip_address {string} -- IP address of the Mainframe server.

        Returns:
            tuple -- stdout, stderr, and return code of the recall command.
        """
        Log().logger.info(LogM.RECALL.value % dataset_name)
        ftp_recall = 'cd ' + dataset_name

        Log().logger.debug(LogM.COMMAND.value % (job_name, ftp_recall))
        stdout, stderr, return_code = self.execute_ftp_command(
            ftp_recall, ip_address)

        return stdout, stderr, return_code

    def dscreate(self, record):
        """
        """
        options = '-o ' + record[MCol.DSORG.value]
        options += ' -b ' + record[MCol.BLKSIZE.value]
        options += ' -l ' + record[MCol.LRECL.value]

        if 'F' in record[MCol.RECFM.value] and record[
                MCol.LRECL.value] == '80' and record[
                    MCol.COPYBOOK.value] == 'L_80.convcpy':
            options += ' -f L'
        else:
            options += ' -f ' + record[MCol.RECFM.value]

        dscreate = 'dscreate ' + options + ' ' + record[MCol.DSN.value]

        Log().logger.info(LogM.COMMAND.value % ('migration', dscreate))
        _, _, rc = ShellHandler().execute_command(dscreate, 'migration')

        return rc

    def dsdelete(self, record):
        """
        """
        dsdelete = 'dsdelete ' + record[MCol.DSN.value]

        Log().logger.info(LogM.COMMAND.value % ('migration', dsdelete))
        _, _, rc = ShellHandler().execute_command(dsdelete, 'migration')

        return rc

    def dsmigin(self, record, context, src='', dst='', member=''):
        """

        Arguments:
            record {string} -- Record length.
            context {string} -- Context.
            src {string} -- Source file.
            dst {string} -- Destination file.
            member {string} -- Member.
        """
        if src == '' and dst == '':

            src = context.datasets_directory + '/' + record[MCol.DSN.value]

            if context.conversion == ' -C ':
                dst = context.conversion_directory + '/' + record[
                    MCol.DSN.value]
            else:
                dst = record[MCol.DSN.value]

        options = ' -e ' + context.encoding_code
        options += context.conversion
        options += ' -sosi 6'
        options += ' -z'

        if record[MCol.COPYBOOK.value] == '':
            Log().logger.info(LogM.COPYBOOK_DEFAULT.value %
                              record[MCol.DSN.value])
            options += ' -s ' + record[MCol.DSN.value] + '.conv'
        else:
            Log().logger.info(LogM.COPYBOOK_COLUMN.value %
                              record[MCol.COPYBOOK.value])
            options += ' -s ' + record[MCol.COPYBOOK.value].rsplit(
                '.', 1)[0] + '.conv'

        if 'F' in record[MCol.RECFM.value] and record[
                MCol.LRECL.value] == '80' and record[
                    MCol.COPYBOOK.value] == 'L_80.convcpy':
            options += ' -f L'
        elif record[MCol.RECFM.value] == 'VBM':
            options += ' -f VB'
        else:
            options += ' -f ' + record[MCol.RECFM.value]

        if record[MCol.DSORG.value] == 'PO':
            options += ' -o PS'
            options += ' -m ' + member
        elif record[MCol.DSORG.value] == 'PS':
            options += ' -o ' + record[MCol.DSORG.value]

        if record[MCol.DSORG.value] == 'VSAM':
            options += ' -l ' + record[MCol.MAXLRECL.value]
            options += ' -R'
        else:
            options += ' -l ' + record[MCol.LRECL.value]
            options += ' -b ' + record[MCol.BLKSIZE.value]
            options += context.force

        dsmigin = 'dsmigin ' + src + ' ' + dst + options

        Log().logger.info(LogM.COMMAND.value % ('migration', dsmigin))
        _, _, rc = ShellHandler().execute_command(dsmigin, 'migration')

        return rc

    def idcams_define(self, record, context):
        """

        Arguments:
            record {string} -- Record length.
            context {string} -- Context.

        Returns:
            integer -- Return code of the idcams define command.
        """
        src = record[MCol.DSN.value]

        options = ' -o ' + record[MCol.VSAM.value]
        options += ' -l ' + record[MCol.AVGLRECL.value]
        options += ',' + record[MCol.MAXLRECL.value]
        options += ' -k ' + record[MCol.KEYLEN.value]
        options += ',' + record[MCol.KEYOFF.value]
        options += ' -t CL'

        if 'CATALOG' in context.enable_column_list:
            Log().logger.info(LogM.CATALOG_COLUMN.value %
                              record[MCol.CATALOG.value])
            options += ' -c ' + record[MCol.CATALOG.value]
        else:
            Log().logger.info(LogM.CATALOG_DEFAULT.value)
            options += ' -c SYS1.MASTER.ICFCAT'

        if 'VOLSER' in context.enable_column_list:
            if record[MCol.VOLSER.value] in ('Migrated', 'Pseudo', 'Tape'):
                Log().logger.info(LogM.VOLSER_SET_DEFAULT.value %
                                  record[MCol.VOLSER.value])
                options += ' -v DEFVOL'
            else:
                Log().logger.info(LogM.VOLSER_COLUMN.value %
                                  record[MCol.VOLSER.value])
                options += ' -v ' + record[MCol.VOLSER.value]
        else:
            Log().logger.info(LogM.VOLSER_DEFAULT.value)
            options += ' -v DEFVOL'

        idcams_define = 'idcams define' + ' -n ' + src + options

        Log().logger.info(LogM.COMMAND.value % ('migration', idcams_define))
        _, _, rc = ShellHandler().execute_command(idcams_define, 'migration')

        # Retry with -O option if failed
        if rc != 0:
            options += ' -O'
            idcams_define = 'idcams define' + ' -n ' + src + options

            Log().logger.info(LogM.COMMAND.value %
                               ('migration', idcams_define))
            _, _, rc = ShellHandler().execute_command(idcams_define,
                                                      'migration')

        return rc

    def idcams_delete(self, record):
        """

        Arguments:
            record {string} -- Record length.

        Returns:
            integer -- Return code of the idcams delete command.
        """
        options = ' -t CL'

        idcams_delete = 'idcams delete ' + ' -n ' + record[
            MCol.DSN.value] + options

        Log().logger.info(LogM.COMMAND.value % ('migration', idcams_delete))
        _, _, rc = ShellHandler().execute_command(idcams_delete, 'migration')

        return rc
