#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the FileHandler module.
"""

# Generic/Built-in modules
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestGetFiles(object):
    """Test cases for the method get_files.

    Fixtures:
        init_pwd
        shared

    Tests:
        test_directory_not_found_error
        test_file_not_found_error
    """

    @staticmethod
    @pytest.fixture
    def shared():
        """Specify the absolute path of the shared directory.
        """
        pwd = os.getcwd() + '/tests/shared/'
        return pwd

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_directory_not_found_error(shared):
        """Test with a directory that does not exist.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        with pytest.raises(FileNotFoundError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_file_not_found_error(shared):
        """Test with a file that does not exist.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        with pytest.raises(FileNotFoundError):
            Main().run()