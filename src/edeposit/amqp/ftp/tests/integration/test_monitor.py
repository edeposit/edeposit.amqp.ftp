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
import edeposit.amqp.ftp.request_parser as request_parser


#= Variables ==================================================================
USERNAME = get_random_str()
PASSWORD = get_random_str()
ftp = None


#= Tests ======================================================================
def setup_module(module):
    api.add_user(USERNAME, PASSWORD)

    global ftp
    ftp = ftputil.FTPHost(settings.SERVER_ADDRESS, USERNAME, PASSWORD)


def teardown_module(module):
    api.remove_user(USERNAME)

    global ftp
    ftp.close()


def get_ftp_handler():
    global ftp

    return ftp


def upload_files(path="src/edeposit/amqp/ftp/tests/integration/data"):
    ftp = get_ftp_handler()

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
    ftp = get_ftp_handler()

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


def test_server():
    msg = "Try to run the initializer script first."
    assert os.path.exists(settings.CONF_PATH), msg
    assert os.path.exists(settings.LOGIN_FILE), msg
    assert os.path.exists(settings.DATA_PATH), msg
    assert os.path.exists(settings.LOG_PATH), msg
    assert os.path.exists(settings.LOG_FILE), msg


def test_monitor():
    upload_files()
    remove_lock()
    out = process_files()

    reqs = out.requests
    assert len(reqs) == 8, "Didn't received expected amount of items!"

    pairs = filter(lambda x: isinstance(x, structures.DataPair), reqs)
    assert pairs

    standalone = filter(
        lambda x: isinstance(x, structures.MetadataFile),
        reqs
    )

    assert len(standalone) == 2
    standalone_names = map(lambda x: x.parsed_data.nazev, standalone)

    assert standalone[0].parsed_data.ISBN == '80-86056-31-7'
    assert standalone[1].parsed_data.ISBN == '80-86056-31-7'

    assert 'standalone_meta.yaml' in standalone_names
    assert "standalone_meta.xml" in standalone_names

    ftp = get_ftp_handler()
    assert not ftp.path.isfile("example_data/advanced/bad.json")


def test_isbn_pairing():
    settings.SAME_NAME_DIR_PAIRING = False
    settings.SAME_DIR_PAIRING = False
    settings.ISBN_PAIRING = True
    reload(request_parser)

    upload_files()
    remove_lock()
    out = process_files()

    pair = filter(lambda x: isinstance(x, structures.DataPair), out.requests)
    assert len(pair) == 1

    m_fn = request_parser._just_name(pair[0].metadata_file.filename)
    d_fn = request_parser._just_name(pair[0].ebook_file.filename)

    assert m_fn == d_fn
    assert m_fn == "80-86056-31-7"


def test_same_dir_pairing():
    settings.SAME_NAME_DIR_PAIRING = False
    settings.SAME_DIR_PAIRING = True
    settings.ISBN_PAIRING = False
    reload(request_parser)

    upload_files()
    remove_lock()
    out = process_files()

    pair = filter(lambda x: isinstance(x, structures.DataPair), out.requests)
    assert len(pair) == 1

    m_fn = request_parser._just_name(pair[0].metadata_file.filename)
    d_fn = request_parser._just_name(pair[0].ebook_file.filename)

    assert m_fn == "whatever"
    assert d_fn == "meta"


def test_same_name_dir_pairing():
    settings.SAME_NAME_DIR_PAIRING = True
    settings.SAME_DIR_PAIRING = False
    settings.ISBN_PAIRING = False
    reload(request_parser)

    upload_files()
    remove_lock()
    out = process_files()

    pair = filter(lambda x: isinstance(x, structures.DataPair), out.requests)
    assert len(pair) == 1

    m_fn = request_parser._just_name(pair[0].metadata_file.filename)
    d_fn = request_parser._just_name(pair[0].ebook_file.filename)

    assert m_fn == "samename"
    assert d_fn == "samename"

    assert pair[0].metadata_file.parsed_data.nazev == "samename.json"


def test_leave_bad_files():
    settings.LEAVE_BAD_FILES = False
    reload(request_parser)

    ftp = get_ftp_handler()
    upload_files()
    remove_lock()
    process_files()

    assert not ftp.path.isfile("example_data/advanced/bad.json")

    settings.LEAVE_BAD_FILES = True


def test_import_log_disabled():
    settings.CREATE_IMPORT_LOG = False
    reload(request_parser)

    ftp = get_ftp_handler()
    if ftp.path.isfile(settings.USER_IMPORT_LOG):
        ftp.remove(settings.USER_IMPORT_LOG)

    upload_files()
    remove_lock()
    process_files()

    assert not ftp.path.isfile(settings.USER_IMPORT_LOG)


def test_import_log_enabled():
    settings.CREATE_IMPORT_LOG = True
    reload(request_parser)

    ftp = get_ftp_handler()
    if ftp.path.isfile(settings.USER_IMPORT_LOG):
        ftp.remove(settings.USER_IMPORT_LOG)

    upload_files()
    remove_lock()
    process_files()

    assert ftp.path.isfile(settings.USER_IMPORT_LOG)

    with ftp.open(settings.USER_IMPORT_LOG) as log:
        user_log = log.read()

        assert len(user_log.splitlines()) > 5, "Userlog is not working!"
        assert "Error: Import only partially successful." in user_log
        assert "--- Errors ---" in user_log
        assert "--- Successfully imported files ---"


def test_error_log():
    upload_files()
    remove_lock()
    process_files()

    ftp = get_ftp_handler()
    assert ftp.path.isfile(settings.USER_ERROR_LOG)

    with ftp.open(settings.USER_ERROR_LOG) as elog:
        error_log = elog.read()

        assert error_log.splitlines(), "Error log is not working!"
        assert "bad.json" in error_log
