#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os

import pytest
import ftputil
from shared import get_random_str

import edeposit.amqp.ftp.api as api
import edeposit.amqp.ftp.monitor as monitor


#= Variables ==================================================================
USERNAME = get_random_str()
PASSWORD = get_random_str()


#= Tests ======================================================================
def setup_module(module):
    api.add_user(USERNAME, PASSWORD)


def teardown_module(module):
    api.remove_user(USERNAME)
    api.remove_user("vbftgbjo")
    pass


def upload_files(path="src/edeposit/amqp/ftp/tests/integration/data"):
    ftp = ftputil.FTPHost("localhost", USERNAME, PASSWORD)

    for root, dirs, files in os.walk(path):
        for dn in dirs:
            full_dn = os.path.join(root, dn)
            remote_dn = full_dn[len(path):]
            ftp.makedirs(remote_dn)

        for fn in files:
            full_fn = os.path.join(root, fn)
            remote_fn = full_fn[len(path):]
            ftp.upload(full_fn, remote_fn)


def test_monitor():
    upload_files()

