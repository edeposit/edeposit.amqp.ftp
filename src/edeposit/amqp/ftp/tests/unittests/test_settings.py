#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import edeposit.amqp.ftp.settings as settings


#= Variables ==================================================================
STRINGS = [
    "BASE_PATH",
    "CONF_PATH",
    "LOG_PATH",
    "DATA_PATH",
    "CONF_FILE",
    "LOGIN_FILE",
    "LOG_FILE",
    "LOCK_FILENAME",
    "USER_ERROR_LOG",
    "USER_IMPORT_LOG",
    "LOCK_FILE_CONTENT",
    "SERVER_ADDRESS"
]

BOOLEAN = [
    "SAME_NAME_DIR_PAIRING",
    "SAME_DIR_PAIRING",
    "ISBN_PAIRING",
    "LOCK_ONLY_IN_HOME",
    "CREATE_IMPORT_LOG"
]

NUMERIC = [
    "PROFTPD_USERS_GID"
]

ALL_VARS = STRINGS + BOOLEAN + NUMERIC


#= Tests ======================================================================
def test_variable_presence():
    for var in ALL_VARS:
        hasattr(settings, var)
        assert getattr(settings, var) is not None


def test_strings():
    for var in STRINGS:
        assert type(getattr(settings, var)) in [str, unicode]

    assert settings.CONF_FILE.startswith(settings.CONF_PATH)
    assert settings.LOGIN_FILE.startswith(settings.CONF_PATH)
    assert settings.LOG_FILE.startswith(settings.LOG_PATH)


def test_booleans():
    for var in BOOLEAN:
        assert isinstance(getattr(settings, var), bool)


def test_numerics():
    for var in NUMERIC:
        int(getattr(settings, var))
