#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the CSV module.
"""

# Generic/Built-in modules
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestCheckHeaders (object):
    """

    Fixtures:
        init_pwd
        shared

    Tests:
        test_headers_dsn_only
        test_headers_extra
        test_headers_missing
        test_headers_multiple_typos
        test_headers_ok
        test_headers_one_typo
    """

    @staticmethod
    @pytest.fixture
    def init_pwd():
        """Specify the absolute path to the current test directory.
        """
        pwd = os.getcwd() + '/tests/unit/csv/'
        return pwd

    @staticmethod
    @pytest.fixture
    def shared():
        """Specify the absolute path of the shared directory.
        """
        pwd = os.getcwd() + '/tests/shared/'
        return pwd

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_headers_dsn_only(shared):
        """Test with an CSV file that contains DSN headers only.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
            
        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_headers_extra(shared):
        """Test with an CSV file that contains too many headers.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
            
        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_headers_missing(shared):
        """Test with an CSV file which has missing headers.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
            
        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_headers_multiple_typos(shared):
        """Test with an CSV file where multiple headers contain some typos.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
            
        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_headers_ok(shared):
        """Test with an CSV file where the headers are correct.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
            
        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_headers_one_typo(shared):
        """Test with an CSV file where one header contain a typo.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
            
        assert Main().run() == 0