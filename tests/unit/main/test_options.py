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


class TestOptions(object):
    """Test cases for some of the command line options.

    Fixtures:
        shared

    Tests:
        test_dsn
        test_encoding_code
        test_help
        test_no_option
        test_tag
        test_version
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
    def test_dsn(shared):
        """Test with the -d, --dsn option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--dsn', ''])

        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_encoding_code(shared):
        """Test with the -e, --encoding-code option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--encoding-code', 'US'])

        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_help():
        """Test with the --help option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--help')

        with pytest.raises(SystemExit):
            Main().run()

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_no_option():
        """Test with no option to see help message output.
        """
        sys.argv = [sys.argv[0]]

        with pytest.raises(SystemExit):
            Main().run()

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_tag(shared):
        """Test with the --tag option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--tag', 'test'])

        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_version():
        """Test with the --version option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--version')

        with pytest.raises(SystemExit):
            Main().run()
