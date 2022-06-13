#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the Main module.
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
    """Test cases for the argparse module errors.

    Fixtures:
        init_pwd

    Tests:
        test_missing_csv_error
        test_missing_work_directory_error
        test_csv_invalid_type_error
        test_working_directory_invalid_type_error
        test_dsn_invalid_type_error
        test_encoding_code_invalid_type_error
        test_encoding_code_invalid_value_error
        test_enable_column_invalid_type_error
        test_generations_invalid_type_error
        test_ip_address_invalid_type_error
        test_listcat_gen_invalid_type_error
        test_log_level_invalid_type_error
        test_log_level_invalid_value_error
        test_number_invalid_type_error
        test_prefix_invalid_type_error
        test_tag_invalid_type_error
        test_invalid_option_error
    """

    @staticmethod
    @pytest.fixture
    def init_pwd():
        """
        """
        pwd = os.getcwd() + '/tests/unit/main/'
        return pwd

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
    def test_missing_csv_error(shared):
        """Test with the required option '-c, --csv' missing.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_missing_work_directory_error(shared):
        """Test with the required option '-w, --working-directory' missing.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_csv_invalid_type_error(shared):
        """Test with an invalid type for the '-c, --csv' option instead of a string.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + '0'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_working_directory_invalid_type_error(shared):
        """Test with an invalid type specified for the '-w, --working-directory' option instead of a string.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        #TODO Test if 0 is considered as a str or int in this scenario
        sys.argv.extend(['--working-directory', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_dsn_invalid_type_error(shared):
        """Test with an invalid type specified for the '-d, --dsn' option instead of a string.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--dsn', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_encoding_code_invalid_type_error(shared):
        """Test with an invalid type specified for the '-e, --encoding-code' option instead of a string.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--encoding-code', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_encoding_code_invalid_value_error(shared):
        """Test with an invalid value specified for the '-e, --encoding-code' option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--encoding-code', 'FR'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_enable_column_invalid_type_error(shared):
        """Test with an invalid type specified for the '--enable-column' option instead of an integer.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--enable-column', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_generations_invalid_type_error(shared):
        """Test with an invalid type specified for the '-g, --generations' option instead of an integer.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--generations', 'a'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_ip_address_invalid_type_error(shared):
        """Test with an invalid type specified for the '-i, --ip-address' option instead of a string.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_listcat_gen_invalid_type_error(shared):
        """Test with an invalid type specified for the '--listcat-gen' option instead of a string.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--listcat-gen', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()
    
    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_log_level_invalid_type_error(shared):
        """Test with an invalid type specified for the '-l, --log-level' option instead of a string.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--log-level', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()
    
    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_log_level_invalid_value_error(shared):
        """Test with an invalid value specified for the '-l, --log-level' option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--log-level', 'AMAZING'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_number_invalid_type_error(shared):
        """Test with an invalid type specified for the '-n, --number' option instead of an integer.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--number', 'a'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_prefix_invalid_type_error(shared):
        """Test with an invalid type specified for the '-p, --prefix' option instead of an integer.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--prefix', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_tag_invalid_type_error(shared):
        """Test with an invalid type specified for the '-t, --tag' option instead of an integer.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--tag', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_invalid_option_error(shared):
        """Test with an option that does not exist.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--invalid-option', '0'])

        with pytest.raises(argparse.ArgumentError):
            Main().run()