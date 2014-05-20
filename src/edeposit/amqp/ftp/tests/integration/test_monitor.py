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
import edeposit.amqp.ftp.settings as settings
import edeposit.amqp.ftp.structures as structures


#= Variables ==================================================================
USERNAME = get_random_str()
PASSWORD = get_random_str()


#= Tests ======================================================================
def setup_module(module):
    api.add_user(USERNAME, PASSWORD)


def teardown_module(module):
    pass
    api.remove_user(USERNAME)


def upload_files(path="src/edeposit/amqp/ftp/tests/integration/data"):
    with ftputil.FTPHost("localhost", USERNAME, PASSWORD) as ftp:
        for root, dirs, files in os.walk(path):
            for dn in dirs:
                full_dn = os.path.join(root, dn)
                remote_dn = full_dn[len(path):]
                ftp.makedirs(remote_dn)

            for fn in files:
                full_fn = os.path.join(root, fn)
                remote_fn = full_fn[len(path):]
                ftp.upload(full_fn, remote_fn)


def remove_lock():
    with ftputil.FTPHost("localhost", USERNAME, PASSWORD) as ftp:
        # check if lock exists
        assert ftp.path.isfile(settings.LOCK_FILENAME), "Lock not found!"
        ftp.remove(settings.LOCK_FILENAME)


def process_files():
    out = None
    with open(settings.LOG_FILE) as f:
        lines = f.read().splitlines()[-5:]
        for o in monitor.process_log(lines):
            out = o

    assert isinstance(out, structures.ImportRequest), "Bad structure retuned!"
    assert out.username == USERNAME, "Badly parsed username!"

    return out


def test_monitor():
    upload_files()
    remove_lock()
    out = process_files()

    reqs = out.requests
    assert len(reqs) >= 4, "Didn't received expected amount of items!"

    pairs = filter(lambda x: isinstance(x, structures.DataPair), reqs)
    assert pairs

    # test whether the pairs hafe same filename
    for pair in pairs:
        m_fn = monitor._just_name(pair.metadata_file.filename)
        d_fn = monitor._just_name(pair.ebook_file.filename)
        assert m_fn == d_fn

    standalone = filter(
        lambda x: isinstance(x, structures.MetadataFile) and
                    x.filename.endswith("standalone_meta.json"),
        reqs
    )

    assert standalone
    assert standalone[0].parsed_data.ISBN == '80-86056-31-7'


def test_isbn_pairing():
    settings.SAME_NAME_DIR_PAIRING = False
    settings.SAME_DIR_PAIRING = False
    settings.ISBN_PAIRING = True

    upload_files()
    remove_lock()
    out = process_files()

    pair = filter(lambda x: isinstance(x, structures.DataPair), out.requests)
    assert len(pair) == 1

    m_fn = monitor._just_name(pair[0].metadata_file.filename)
    d_fn = monitor._just_name(pair[0].ebook_file.filename)

    assert m_fn == d_fn
    assert m_fn == "80-86056-31-7"
