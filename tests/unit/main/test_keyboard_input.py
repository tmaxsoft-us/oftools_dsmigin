#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the Main module.
"""

# Generic/Built-in modules
import os
import signal
import subprocess
import sys

# Third-party modules
import pytest

# Owned modules


class TestKeyboardInput(object):
    """Test cases for the KeyboardInterrupt exception.

    Fixtures:
        shared

    Tests:
        test_ctrl_c
        test_ctrl_backslash
    """

    @staticmethod
    @pytest.fixture
    def shared():
        """Specify the absolute path of the shared directory.
        """
        pwd = os.getcwd() + '/tests/shared/'
        return pwd

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_ctrl_c(shared):
        """Test with a Ctrl + C input to send the signal SIGINT and raise the KeyboardInterrupt exception to cancel the current dataset processing.
          """
        sys.argv = ['oftools_dsmigin']
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        process = subprocess.Popen(sys.argv,
                                   universal_newlines=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        process.send_signal(signal.SIGINT)
        process.communicate()

        assert process.returncode == -2

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_ctrl_backslash(shared):
        """Test with a Ctrl + \\ input to send the signal SIGQUIT and fully abort the program execution.
          """
        sys.argv = ['oftools_dsmigin']
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        process = subprocess.Popen(sys.argv,
                                   universal_newlines=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        process.send_signal(signal.SIGQUIT)
        process.communicate()

        assert process.returncode == -3
