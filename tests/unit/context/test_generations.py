#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the Context module.
"""

# Generic/Built-in modules
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestGenerations(object):
    """

    Fixtures:
        init_pwd

    Tests:
        test_number
        test_sign_error
    """

    @staticmethod
    @pytest.fixture
    def init_pwd():
        """
        """
        pwd = os.getcwd() + '/tests/unit/context/'
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
    def test_number(shared):
        """Test with a positive value for the generations option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--generations', '2'])

        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    @pytest.mark.xfail
    def test_sign_error(shared):
        """Test with a negative value for the generations option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--generations', '-1'])

        with pytest.raises(SystemError):
            Main().run()