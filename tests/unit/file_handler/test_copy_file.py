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


class TestCopyFile(object):
    """Test cases for the method copy_file.
    
    Fixtures:
        shared

    Tests:
        test_os_error
        test_shutil_same_file_error
    """

    @staticmethod
    @pytest.fixture
    def shared():
        """Specify the absolute path of the shared directory.
        """
        pwd = os.getcwd() + '/tests/shared/'
        return pwd

    # Python built-in exceptions

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_os_error(shared):
        """Test with...
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        # OSError
        assert Main().run() == -1

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_shutil_same_file_error(shared):
        """Test with...
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        # shutil.SameFileError
        assert Main().run() == 1
