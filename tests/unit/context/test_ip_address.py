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


class TestIPAddress(object):
    """

    Fixtures:
        init_pwd
        shared

    Tests:
        test_ipv4
        test_ipv6
        test_ip_error
    """

    @staticmethod
    @pytest.fixture
    def init_pwd():
        """Specify the absolute path to the current test directory.
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
    def test_ipv4(shared):
        """Test with an IPv4 ip address.
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
    def test_ipv6(shared):
        """Test with an IPv6 ip address.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '2001:0db8:0000:0000:0000:ff00:0042:8329'])
        sys.argv.extend(['--listcat'])

        assert Main().run() == 0

    @staticmethod
    @pytest.mark.skip(reason='Test not currently supported')
    @pytest.mark.xfail
    def test_ip_error(shared):
        """Test with an incorrect ip address.
        """
        sys.argv = [sys.argv[0]]
        sys.argv.append('--clear')
        sys.argv.extend(['--log-level', 'DEBUG'])
        sys.argv.extend(['--csv', shared + 'working_directory/default.csv'])
        sys.argv.extend(['--working-directory', shared + 'working_directory'])
        sys.argv.extend(['--ip-address', '192.168.0'])
        sys.argv.extend(['--listcat'])

        with pytest.raises(SystemError):
            Main().run()