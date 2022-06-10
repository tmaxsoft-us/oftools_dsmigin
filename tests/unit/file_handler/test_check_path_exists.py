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


class TestCheckPathExists(object):
    """Test cases for the method check_path_exists.
    
    Fixtures:
        shared

    Tests:
        test_file_not_found_error
        test_file_not_found_skip_error
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
    def test_file_not_found_error(shared):
        """Test with a source that does not exist.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        with pytest.raises(FileNotFoundError):
            Main().run()

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_file_not_found_skip_error(shared):
        """Test with a source that does not exist and the skip flag being used.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.append('--skip')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        assert Main().run() == 0