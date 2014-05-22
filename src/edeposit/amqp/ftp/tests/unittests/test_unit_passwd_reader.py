#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import binascii

import edeposit.amqp.ftp.passwd_reader as passwd_reader


#= Variables ==================================================================
TEST_DATA = """xex:$passhash:2000:2000::/home/ftp/xex:/bin/false
xax:$passhash:2000:2000::/home/ftp/xax:/bin/false"""
RAND_FN = "/tmp/" + binascii.b2a_hex(os.urandom(15))


#= Functions & objects ========================================================
def test_load_users():
    with open(RAND_FN, "w") as f:
        f.write(TEST_DATA)

    data = passwd_reader.load_users(RAND_FN)

    assert "xex" in data
    assert "xax" in data

    assert data["xex"]["pass_hash"] == "$passhash"
    assert data["xex"]["uid"] == "2000"
    assert data["xex"]["gid"] == "2000"
    assert data["xex"]["full_name"] == ""
    assert data["xex"]["home"] == "/home/ftp/xex"
    assert data["xex"]["shell"] == "/bin/false"


def test_save_users():
    # make file blank
    with open(RAND_FN, "w") as f:
        f.write("")

    passwd_reader.save_users(
        {
            "xex": {
                "pass_hash": "$passhash",
                "uid": "2000",
                "gid": "2000",
                "full_name": "",
                "home": "/home/ftp/xex",
                "shell": "/bin/false"
            },
            "xax": {
                "pass_hash": "$passhash",
                "uid": "2000",
                "gid": "2000",
                "full_name": "",
                "home": "/home/ftp/xax",
                "shell": "/bin/false"
            }
        },
        RAND_FN
    )

    test_load_users()


def teardown_module():
    os.remove(RAND_FN)
