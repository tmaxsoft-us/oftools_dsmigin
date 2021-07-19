#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
"""

# Generic/Built-in modules
import argparse
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestArgParseErrors(object):
    """

    Fixtures:
        init_pwd

    Tests:
        test_missing_csv_error
        test_missing_work_directory_error
        test_csv_invalid_type_error
        test_invalid_option_error
    """

    @pytest.fixture
    def init_pwd(self):
        """
        """
        pwd = os.getcwd() + '/tests/unit/main/'
        return pwd

    @pytest.mark.xfail
    def test_missing_csv_error(self):
        """Test with the csv required argument missing.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @pytest.mark.xfail
    def test_missing_work_directory_error(self, init_pwd):
        """Test with the work directory required argument missing.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', init_pwd + 'default.csv'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @pytest.mark.xfail
    def test_csv_invalid_type_error(self):
        """Test with a number specified for the csv option instead of a string.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])
        sys.argv.extend(['--csv', '1'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()
    
    #TODO Could create the test just above for all the options

    @pytest.mark.xfail
    def test_invalid_option_error(self):
        """Test with an option that does not exist.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])
        sys.argv.extend(['--invalid-option', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()