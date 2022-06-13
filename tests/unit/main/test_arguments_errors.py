#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the Main module.
"""

# Generic/Built-in modules
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestArgumentsErrors(object):
    """Test cases for arguments errors.

    Fixtures:
        shared

    Tests:
        test_csv_type_error
        test_listcat_missing_ip_address_error
        test_ftp_missing_ip_address_error
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
    def test_csv_type_error(shared):
        """Test with the option '-c, --csv' specified, not being a file with a .csv extension.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.txt'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        with pytest.raises(TypeError):
            Main().run()

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_listcat_missing_ip_address_error(shared):
        """Test with the option '-L, --listcat' specified, but no '-i , --ip-address' option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--listcat'])

        assert Main().run() == 0

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_ftp_missing_ip_address_error(shared):
        """Test with the option '-F, --ftp' specified, but no '-i, --ip-address' option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ftp'])

        with pytest.raises(SystemError):
            Main().run()
