#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
"""

# Generic/Built-in modules
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestArgumentsErrors(object):
    """

    Fixtures:
        init_pwd

    Tests:
        test_csv_missing_ip_address_error
        test_download_missing_ip_address_error
        test_download_missing_number_error
        test_migration_missing_copybook_directory_error
        test_ip_address_format_error
        test_number_sign_error
        test_listcat_result_type_error
        test_listcat_result_index_error
    """

    @pytest.fixture
    def init_pwd(self):
        """
        """
        pwd = os.getcwd() + '/tests/unit/main/'
        return pwd

    @pytest.mark.xfail
    def test_csv_missing_ip_address_error(self, init_pwd):
        """Test with the csv option specified but no ip_address option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])
        sys.argv.extend(['--csv', init_pwd + 'default.csv'])

        with pytest.raises(SystemError):
            Main().run()

    @pytest.mark.xfail
    def test_download_missing_ip_address_error(self, init_pwd):
        """Test with the download option specified but no ip_address option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])
        sys.argv.extend(['--csv', init_pwd + 'default.csv'])
        sys.argv.extend(['--download'])

        with pytest.raises(SystemError):
            Main().run()
    
    @pytest.mark.xfail
    def test_download_missing_number_error(self, init_pwd):
        """Test with the download option specified but no number option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])
        sys.argv.extend(['--csv', init_pwd + 'default.csv'])
        sys.argv.extend(['--download'])
        sys.argv.extend(['--ip-address'])

        with pytest.raises(SystemError):
            Main().run()

    @pytest.mark.xfail
    def test_migration_missing_copybook_directory_error(self, init_pwd):
        """Test with the migration option specified but no copybook directory option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])
        sys.argv.extend(['--csv', init_pwd + 'default.csv'])
        sys.argv.extend(['--migration'])

        with pytest.raises(SystemError):
            Main().run()

    @pytest.mark.xfail
    def test_ip_address_format_error(self, init_pwd):
        """Test with a listcat result file without extension.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])
        sys.argv.extend(['--csv', init_pwd + 'default.csv'])
        sys.argv.extend(['--download'])
        sys.argv.extend(['--number', '-1'])

        with pytest.raises(SystemError):
            Main().run()

    @pytest.mark.xfail
    def test_number_sign_error(self, init_pwd):
        """Test with a listcat result file without extension.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])
        sys.argv.extend(['--csv', init_pwd + 'default.csv'])
        sys.argv.extend(['--download'])
        sys.argv.extend(['--number', '-1'])

        with pytest.raises(SystemError):
            Main().run()
        
    @pytest.mark.xfail
    def test_listcat_result_type_error(self, init_pwd):
        """Test with a listcat result file with the wrong extension.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])
        sys.argv.extend(['--csv', init_pwd + 'default.csv'])
        sys.argv.extend(['--listcat', init_pwd + 'liscat.log'])

        with pytest.raises(TypeError):
            Main().run()
    
    @pytest.mark.xfail
    def test_listcat_result_index_error(self, init_pwd):
        """Test with a listcat result file without extension.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--work-directory'])
        sys.argv.extend(['--csv', init_pwd + 'default.csv'])
        sys.argv.extend(['--listcat', init_pwd + 'liscat'])

        with pytest.raises(IndexError):
            Main().run()