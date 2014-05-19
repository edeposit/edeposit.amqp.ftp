#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import ftplib
import socket
import telnetlib

import pytest
from shared import get_random_str, is_root

import edeposit.amqp.ftp.api as api


#= Variables ==================================================================
USERNAME = get_random_str()
PASSWORD = get_random_str()


#= Tests ======================================================================

class TestAPI:
    @classmethod
    def setup_class(self):
        """Test whether the proftpd is runnig or not."""
        try:
            telnetlib.Telnet("localhost", 21)
        except socket.error:
            raise AssertionError("Looks like your proftpd is not running!")

    def test_is_valid_username(self):
        assert api._is_valid_username("xex")
        assert api._is_valid_username("Xex")
        assert not api._is_valid_username(",")
        assert not api._is_valid_username("asd/asd")

    def try_login(self):
        """Used to test if it is possible to log into FTP account."""
        ftp = ftplib.FTP('localhost')
        ftp.login(USERNAME, PASSWORD)

    def test_add_user(self):
        is_root()

        with pytest.raises(ftplib.error_perm):
            self.try_login()

        api.add_user(USERNAME, PASSWORD)

        self.try_login()

    def test_change_password(self):
        is_root()

        self.try_login()

        global PASSWORD
        PASSWORD = get_random_str()
        api.change_password(USERNAME, PASSWORD)

        self.try_login()

    def test_remove_user(self):
        is_root()

        api.remove_user(USERNAME)
        with pytest.raises(ftplib.error_perm):
            self.try_login()

    def test_list_users(self):
        users_old = api.list_users()
        api.add_user(USERNAME, PASSWORD)  # removed in .teardown_class()
        users_new = api.list_users()

        assert len(users_old) < len(users_new)

    @classmethod
    def teardown_class(self):
        api.remove_user(USERNAME)
