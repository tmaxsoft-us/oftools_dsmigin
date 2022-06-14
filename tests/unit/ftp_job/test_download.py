#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the FTPJob module.
"""

# Generic/Built-in modules
import os
import sys

# Third-party modules
import pytest

# Owned modules
from ....oftools_dsmigin.Main import Main


class TestDownload(object):
    """Test cases for the method _download.

    Fixtures:
        init_pwd

    Tests:
        test_download_failed_1
        test_download_failed_other
        test_rdw_no_tape
        test_rdw_tape
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
    def test_download_failed_1(shared):
        """Test with a failed dataset download returning -1.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0.1'])
        sys.argv.extend(['--ftp'])
            
        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_download_failed_other(shared):
        """Test with with a failed dataset download not returning -1.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0.1'])
        sys.argv.extend(['--ftp'])
            
        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_rdw_no_tape(shared):
        """Test with the download option rdw used for a dataset not on tape.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0.1'])
        sys.argv.extend(['--ftp'])
            
        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    def test_rdw_tape(shared):
        """Test with the download option rdw used for a dataset on tape.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0.1'])
        sys.argv.extend(['--ftp'])
            
        assert Main().run() == 0