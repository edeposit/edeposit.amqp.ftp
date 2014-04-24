#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
ProFTPD manager used to add/remove users to the FTP server.
"""
import sh

from settings import *


#= Variables ==================================================================
#= Functions & objects ========================================================
def load_users(path=PROFTPD_CONF_PATH + PROFTPD_LOGIN_FILE):
    data = ""
    with open(path) as f:
        data = f.read().splitlines()

    users = {}
    cnt = 1
    for line in data:
        line = line.split(":")

        assert len(line) == 6, "Bad number of fields in '%s', at line %d!" % (
            PROFTPD_CONF_PATH + PROFTPD_LOGIN_FILE,
            cnt
        )

        users[line[0]] = {  # TODO: use namedtuple?
            "pass_hash": line[1],
            "uid": line[2],
            "gid": line[3],
            "full_name": line[4],
            "home": line[5],
            "shell": line[6]
        }

        cnt += 1

    return users


def is_valid_username(username):  # TODO: implement username validation
    return True


def add_user(username, password):
    assert is_valid_username(username), "Invalid username '%s'!" % (username,)

    assert username not in load_users(), "User is already registered!"  # TODO: own exception?

    # TODO: check, if this is first time the script is run


def remove_user(username):
    pass


def change_password(username, password):
    pass


#= Main program ===============================================================
if __name__ == '__main__':  # TODO: debug only, remove later
    # add_user("testovaci_uzivatel")
    print load_users()
