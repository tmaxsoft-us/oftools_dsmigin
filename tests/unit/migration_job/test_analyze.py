#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle some of the test cases for the MigrationJob module.
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
        test_dsorg_invalid
        test_dsorg_not_set
        test_dsmigin_not_set
        test_dsmigin_set_to_f
        test_dsmigin_set_to_n
        test_dsmigin_set_to_y
        test_gdg
        test_ignore_yes
        test_ftpdate_not_set
        test_ps_missing_blksize
        test_ps_missing_lrecl
        test_ps_missing_recfm
        test_vsam_missing_avglrecl
        test_vsam_missing_keylen
        test_vsam_missing_keyoff
        test_vsam_missing_maxlrecl
        test_vsam_missing_recfm
        test_vsam_missing_vsam
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
    def test_dsorg_invalid(shared):
        """Test with an invalid value in the column DSORG.
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
    def test_dsorg_not_set(shared):
        """Test with the column DSORG not set.
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
    def test_dsmigin_not_set(shared):
        """Test with the flag DSMIGIN not set.
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
    def test_dsmigin_set_to_f(shared):
        """Test with the flag DSMIGIN set to 'F' for FORCE.
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
    def test_dsmigin_set_to_n(shared):
        """Test with the flag DSMIGIN set to 'N' for NO.
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
    def test_dsmigin_set_to_y(shared):
        """Test with the flag DSMIGIN set to 'Y' for YES.
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
    def test_ignore_yes(shared):
        """Test with the flag IGNORE set to 'Y' for YES.
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
    def test_ftpdate_not_set(shared):
        """Test with the flag FTPDATE not set.
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
    def test_ps_missing_blksize(shared):
        """Test with a PS dataset but BLKSIZE column not set.
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
    def test_ps_missing_lrecl(shared):
        """Test with a PS dataset but LRECL column not set.
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
    def test_ps_missing_recfm(shared):
        """Test with a PS dataset but RECFM column not set.
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
    def test_vsam_missing_avglrecl(shared):
        """Test with a VSAM dataset but AVGLRECL column not set.
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
    def test_vsam_missing_keylen(shared):
        """Test with a VSAM dataset but KEYLEN column not set.
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
    def test_vsam_missing_keyoff(shared):
        """Test with a VSAM dataset but KEYOFF column not set.
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
    def test_vsam_missing_maxlrecl(shared):
        """Test with a VSAM dataset but MAXLRECL column not set.
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
    def test_vsam_missing_recfm(shared):
        """Test with a VSAM dataset but RECFM column not set.
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
    def test_vsam_missing_vsam(shared):
        """Test with a VSAM dataset but VSAM column not set.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0.1'])
        sys.argv.extend(['--ftp'])

        assert Main().run() == 0
