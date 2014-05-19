#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import ftplib  # TODO: use ftputil (http://ftputil.sschwarzer.net)

import pytest
from shared import get_random_str

import edeposit.amqp.ftp.api as api
import edeposit.amqp.ftp.monitor as monitor


#= Variables ==================================================================
USERNAME = get_random_str()
PASSWORD = get_random_str()
ftp = None


#= Tests ======================================================================
def setup_module(module):
    api.add_user(USERNAME, PASSWORD)


def teardown_module(module):
    # api.remove_user(USERNAME)
    pass


def test_upload():
    global ftp

    ftp = ftplib.FTP("localhost")
    ftp.login(USERNAME, PASSWORD)

    log = []
    path = "src/edeposit/amqp/ftp/tests/integration/data"
    for root, dirs, files in os.walk(path):
        for dn in dirs:
            full_dn = os.path.join(root, dn)
            remote_dn = full_dn[len(path):]
            ftp.mkd(remote_dn)
            # log.append("newd %s -> %s" % (full_dn, remote_dn))

        for fn in files:
            full_fn = os.path.join(root, fn)
            remote_fn = full_fn[len(path):]
            log.append("newf %s -> %s" % (full_fn, remote_fn))

    raise AssertionError("\n".join(log))