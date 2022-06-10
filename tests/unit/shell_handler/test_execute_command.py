#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the ShellHandler module.
"""

# Generic/Built-in modules
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestExecuteCommand(object):
    """Test cases for the method execute_command.
    
    Fixtures:
        shared

    Tests:
        test_system_error
        test_called_process_error
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
    def test_system_error(shared):
        """Test with...
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        assert Main().run() == -1

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_called_process_error(shared):
        """Test with...
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        assert Main().run() == -1
