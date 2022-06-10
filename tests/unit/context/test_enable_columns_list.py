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


class TestEnableColumnsList(object):
    """

    Fixtures:
        init_pwd

    Tests:
        test_enable_columns_list
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
    def test_enable_column_list(shared):
        """Test with the --enable-column option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--enable-column', 'CATALOG:VOLSER'])

        assert Main().run() == 0