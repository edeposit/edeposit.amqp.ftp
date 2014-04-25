#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
ProFTPD manager used to add/remove users to the FTP server.
"""
import os
import os.path
import shutil
from pwd import getpwnam

import sh

from settings import *
from __init__ import reload_configuration


#= Variables ==================================================================
#= Functions & objects ========================================================
def load_users(path=PROFTPD_LOGIN_FILE):
    if not os.path.exists(path):
        return {}

    data = ""
    with open(path) as f:
        data = f.read().splitlines()

    users = {}
    cnt = 1
    for line in data:
        line = line.split(":")

        assert len(line) == 7, "Bad number of fields in '%s', at line %d!" % (
            PROFTPD_LOGIN_FILE,
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


def save_users(users, path=PROFTPD_LOGIN_FILE):
    with open(path, "wt") as f:
        for username, data in users.items():
            pass_line = username + ":" + ":".join([
                data["pass_hash"],
                data["uid"],
                data["gid"],
                data["full_name"],
                data["home"],
                data["shell"]
            ])

            f.write(pass_line + "\n")


def is_valid_username(username):  # TODO: implement username validation
    return True


def add_user(username, password):
    assert is_valid_username(username), "Invalid format of username '%s'!" % (
        username,
    )

    assert username not in load_users(), "User is already registered!"  # TODO: own exception?

    # add new user to the proftpd's passwd file
    home_dir = PROFTPD_DATA_PATH + username
    sh.ftpasswd(
        passwd=True,        # passwd file, not group file
        name=username,
        home=home_dir,      # chroot in PROFTPD_DATA_PATH
        shell="/bin/false",
        uid="2000",         # TODO: parse dynamically?
        stdin=True,         # tell ftpasswd to read password from stdin
        file=PROFTPD_LOGIN_FILE,
        _in=password
    )

    # create home dir if not exists
    if not os.path.exists(home_dir):
        os.makedirs(home_dir, 0777)

    # os.chmod(home_dir, 0777)
    os.chown(home_dir, getpwnam('proftpd').pw_uid, -1)

    # make sure, that the access permissions are set as expected by proftpd
    os.chown(PROFTPD_LOGIN_FILE, getpwnam('proftpd').pw_uid, -1)
    os.chmod(PROFTPD_LOGIN_FILE, 0600)

    reload_configuration()


def remove_user(username):
    users = load_users()

    assert username in users, "Username '%s' not found!" % username

    del users[username]
    save_users(users)

    home_dir = PROFTPD_DATA_PATH + username
    if os.path.exists(home_dir):
        shutil.rmtree(home_dir)


def change_password(username, password):
    assert username in load_users(), "Username '%s' not found!" % username

    sh.ftpasswd(
        "--change-password",
        passwd=True,        # passwd file, not group file
        name=username,
        stdin=True,         # tell ftpasswd to read password from stdin
        file=PROFTPD_LOGIN_FILE,
        _in=password
    )


#= Main program ===============================================================
if __name__ == '__main__':  # TODO: debug only, remove later
    # add_user("testovaci_uzivatel")
    # print add_user("xax", "heslo")
    # remove_user("xux")
    change_password("xax", "heslicko")
