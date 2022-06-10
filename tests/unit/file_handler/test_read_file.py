#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the FileHandler module.
"""

# Generic/Built-in modules
import configparser
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestReadFile(object):
    """Test cases for the method read_file.

    Fixtures:
        init_pwd
        shared

    Tests:
        test_empty_error
        test_file_not_found_error
        test_index_error
        test_is_a_directory_error
        test_permission_error
        test_type_error

        test_duplicate_option_error
        test_duplicate_section_error
        test_missing_section_header_error
    """

    @staticmethod
    @pytest.fixture
    def init_pwd():
        """Specify the absolute path of the current test directory.
        """
        pwd = os.getcwd() + '/tests/unit/file_handler/'
        return pwd

    @staticmethod
    @pytest.fixture
    def shared():
        """Specify the absolute path of the shared directory.
        """
        pwd = os.getcwd() + '/tests/shared/'
        return pwd

    # Python built-in exceptions

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_empty_error(init_pwd, shared):
        """Test with an empty file.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--profile', init_pwd + 'profiles/empty.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        with pytest.raises(SystemError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_file_not_found_error(init_pwd, shared):
        """Test with a file that does not exist.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(
            ['--profile', init_pwd + 'profiles/file_not_found.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        with pytest.raises(FileNotFoundError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_index_error(init_pwd, shared):
        """Test with a file that does not have an extension.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--profile', init_pwd + 'profiles/default'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        with pytest.raises(IndexError):
            Main().run()
 
    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_is_a_directory_error(init_pwd, shared):
        """Test with a directory instead of a file.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(
            ['--profile', init_pwd + 'profiles/is_a_directory.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        with pytest.raises(IsADirectoryError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_permission_error(init_pwd, shared):
        """Test with a file for which the user does not have the necessary permissions.
        """
        os.chmod(init_pwd + 'profiles/permission.prof', 0o200)

        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--profile', init_pwd + 'profiles/permission.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        with pytest.raises(PermissionError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_type_error(init_pwd, shared):
        """Test with a file that does not have a supported extension.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--profile', shared + 'profiles/default_1.prof'])
        sys.argv.extend(['--source', init_pwd + 'sources/sources.type'])

        with pytest.raises(TypeError):
            Main().run()

    # ConfigParser exceptions

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_duplicate_option_error(init_pwd, shared):
        """Test with a profile where there is one section with a duplicate option.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(
            ['--profile', init_pwd + 'profiles/duplicate_option.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        with pytest.raises(configparser.DuplicateOptionError):
            Main().run()
        
    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_duplicate_section_error(init_pwd, shared):
        """Test with a profile where there are two sections with the same name.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(
            ['--profile', init_pwd + 'profiles/duplicate_section.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        with pytest.raises(configparser.DuplicateSectionError):
            Main().run()

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.skip(reason='Test not currently supported')
    def test_missing_section_header_error(init_pwd, shared):
        """Test with a profile where there is no section.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(
            ['--profile', init_pwd + 'profiles/missing_section_header.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        with pytest.raises(configparser.MissingSectionHeaderError):
            Main().run()

    # JSON exceptions
    # Untangle and XML exceptions
