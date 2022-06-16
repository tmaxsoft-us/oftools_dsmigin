#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the ListcatJob module.
"""

# Generic/Built-in modules
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestAnalyze(object):
    """Test cases for the method _analyze.

    Fixtures:
        shared

    Tests:
        test_listcat_not_set
        test_listcat_set_to_f
        test_listcat_set_to_n
        test_listcat_set_to_y
        test_ignore_yes
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
    def test_listcat_not_set(shared):
        """Test with the flag LISTCAT not set.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0.1'])
        sys.argv.extend(['--listcat'])

        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_listcat_set_to_f(shared):
        """Test with the flag LISTCAT set to 'F' for FORCE.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0.1'])
        sys.argv.extend(['--listcat'])

        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_listcat_set_to_n(shared):
        """Test with the flag LISTCAT set to 'N' for NO.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0.1'])
        sys.argv.extend(['--listcat'])

        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_listcat_set_to_y(shared):
        """Test with the flag LISTCAT set to 'Y' for YES.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0.1'])
        sys.argv.extend(['--listcat'])

        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_ignore_yes(shared):
        """Test with the flag IGNORE set to 'Y' for YES.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0.1'])
        sys.argv.extend(['--listcat'])

        assert Main().run() == 0
