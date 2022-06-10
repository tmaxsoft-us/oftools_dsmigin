#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the FileHandler module.
"""

# Generic/Built-in modules
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestWriteFile(object):
    """Test cases for the write_file method.

    Fixtures:
        shared

    Tests:
        test_index_error
        test_is_a_directory_error
        test_permission_error
        test_type_error
    """

    @staticmethod
    @pytest.fixture
    def shared():
        """Specify the absolute path of the shared directory.
        """
        pwd = os.getcwd() + '/tests/shared/'
        return pwd

    # Python built-in exceptions

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_index_error(shared):
        """Test with a file not having an extension.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--profile', shared + 'profiles/default_1.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        # IndexError
        assert Main().run() == -1

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_is_a_directory_error(shared):
        """Test with a directory instead of a file.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(
            ['--profile', shared + 'profiles/default_1.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        # IsADirectoryError
        assert Main().run() == -1

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_permission_error(shared):
        """Test with a file for which the user does not have the necessary permissions.
        """
        os.chmod('', 0o200)

        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--profile', shared + 'profiles/default_1.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        # PermissionError
        assert Main().run() == -1

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_type_error(shared):
        """Test with a file having an unsupported extension.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--profile', shared + 'profiles/default_1.prof'])
        sys.argv.extend(['--source', shared + 'sources/SAMPLE1.cbl'])

        # TypeError
        assert Main().run() == -1