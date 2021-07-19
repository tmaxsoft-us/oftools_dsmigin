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
import subprocess
from shutil import which

# Third-party modules

# Owned modules
from .Context import Context


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
        execute_ftp_command(ftp_command): Separate method to execute FTP command.
    """

    def analyze_ip_address(self, ip_address):
        """Checking the format of the ip address used as a parameter.

        This method is able to detect both IPv4 and IPv6 addresses. It is a really simple pattern analysis.

        Args:
            ip_address: A string, the ip address used as as a parameter.

        Returns:
            A boolean, if the ip address used as input is a fully qualified ip address or not.
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

        return is_valid_ip

    def check_command(self, shell_command):
        """Check if the command exist in the environment using which.

        Returns:
            A boolean, True if the command does not exist and False if the command exist.
        """
        if which(shell_command) is None:
            return True
        else:
            return False

    def execute_shell_command(self, shell_command):
        """Separate method to execute shell command.
        
        This method is dedicated to execute a shell command and it handles exception in case of failure.

        Args:
            shell_command: the actual shell command that needs to be executed.

        Returns:
            A Popen object, which contains the return code and the result of the shell command.
        """
        if self.check_command(shell_command.split()[0]):
            try:
                proc = subprocess.Popen(shell_command,
                                        shell=True,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
                proc.communicate()[0]

                shell_result = proc.stdout.decode('utf_8')
                if ('failed' in shell_result) or (
                        'command not found' in shell_result) or (
                            shell_result == ''):
                    proc = None
            except:
                proc = None
        else:
            proc = None

        return proc

    def execute_ftp_command(self, ftp_command):
        """Separate method to execute FTP command.

        This method is dedicated to execute a ftp command and it handles exception in case of failure. The credentials to open the FTP session are provided through the file .netrc in the home directory. This configuration file needs to be created before the first execution of the tool.
        """
        # ! We might need to use sftp (FTP over SSH) with more security
        # ! By default, connection refused on port 22. After modification of
        # ! the PROFILE to add TCP connection on port 22, still not working

        connection_command = 'lftp << EOF\nlftp ' + Context().ip_address + '\n'
        shell_command = connection_command + ftp_command

        if self.check_command(shell_command.split()[0]):
            try:
                proc = subprocess.Popen(shell_command,
                                        shell=True,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
                proc.communicate()[0]

                shell_result = proc.stdout.decode('utf_8')
                if ('failed' in shell_result) or (
                        'command not found' in shell_result) or (
                            shell_result == ''):
                    proc = None
            except:
                proc = None
        else:
            proc = None

        return proc
