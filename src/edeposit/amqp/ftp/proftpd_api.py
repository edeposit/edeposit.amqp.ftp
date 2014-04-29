#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
ProFTPD manager used to add/remove users to the FTP server.

This module manages the ``ftpd.passwd`` file created by ftpasswd_ script from
profptd_ package.

.. _ftpasswd: http://www.proftpd.org/docs/contrib/ftpasswd.html
.. _proftpd: http://www.proftpd.org

Warning:
    This API supposes, that it has permissions to read/write to `ProFTPD`
    configuration directory and to `root` directory for users.

    You don't have to set the permissions and everything by hand, there is
    :mod:`proftpd_init` script, which can do it for you automatically.
"""
import re
import os
import os.path
import shutil
from pwd import getpwnam

import sh

from settings import *
from __init__ import reload_configuration


#= Variables ==================================================================
#= Functions & objects ========================================================
def _load_users(path=PROFTPD_LOGIN_FILE):
    """
    Load users defined passwd-like format file.

    Args:
        path (str, default settings.PROFTPD_LOGIN_FILE): path of the file,
            which will be loaded (default :attr:`.PROFTPD_LOGIN_FILE`).

    Returns:
        (dict): "username": {"pass_hash": "..", "uid": "..", "gid": "..", \
                "full_name": "..", "home": "..", "shell": ".."}
    """
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


def _save_users(users, path=PROFTPD_LOGIN_FILE):
    """
    Save dictionary with user data to passwd-like file.

    Args:
        users (dict): dictionary with user data. For details look at dict
                      returned from :func:`_load_users`.
        path (str, default settings.PROFTPD_LOGIN_FILE): path of the file,
            which will be loaded (default :attr:`.PROFTPD_LOGIN_FILE`).
    """
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


def _is_valid_username(username):
    """
    Check if username consist from characters "a-zA-Z0-9._-".

    Args:
        username (str): username.
    """
    return re.search("^[a-zA-Z0-9\.\_\-]*$", username)


def add_user(username, password):
    """
    Add new user.

    Adds record to passwd-like file for ProFTPD, creates home directory and
    sets permissions for important files.

    Args:
        username (str): ..
        password (str): ..
    """
    assert _is_valid_username(username), \
            "Invalid format of username '%s'!" % username

    assert username not in _load_users(), \
            "User '%s' is already registered!" % username

    # add new user to the proftpd's passwd file
    home_dir = PROFTPD_DATA_PATH + username
    sh.ftpasswd(
        passwd=True,        # passwd file, not group file
        name=username,
        home=home_dir,      # chroot in PROFTPD_DATA_PATH
        shell="/bin/false",
        uid="2000",         # TODO: parse dynamically?
        gid="2000",
        stdin=True,         # tell ftpasswd to read password from stdin
        file=PROFTPD_LOGIN_FILE,
        _in=password
    )

    # create home dir if not exists
    if not os.path.exists(home_dir):
        os.makedirs(home_dir, 0775)

    # os.chmod(home_dir, 0777)
    # I am using 2000 GID for all our users - this GID shouldn't be used by
    # other group!
    os.chown(home_dir, getpwnam('proftpd').pw_uid, 2000)
    os.chmod(home_dir, 0775)

    # make sure, that the access permissions are set as expected by proftpd
    os.chown(PROFTPD_LOGIN_FILE, getpwnam('proftpd').pw_uid, -1)
    os.chmod(PROFTPD_LOGIN_FILE, 0600)

    reload_configuration()


def remove_user(username):
    """
    Remove user, his home directory and so on..

    Args:
        username (str): ..
    """
    users = _load_users()

    assert username in users, "Username '%s' not found!" % username

    # remove user from passwd file
    del users[username]
    _save_users(users)

    # remove home directory
    home_dir = PROFTPD_DATA_PATH + username
    if os.path.exists(home_dir):
        shutil.rmtree(home_dir)

    reload_configuration()


def change_password(username, new_password):
    """
    Change password for given `username`.

    Args:
        username (str): ..
        new_password (str): ..
    """
    assert username in _load_users(), "Username '%s' not found!" % username

    sh.ftpasswd(
        "--change-password",
        passwd=True,        # passwd file, not group file
        name=username,
        stdin=True,         # tell ftpasswd to read password from stdin
        file=PROFTPD_LOGIN_FILE,
        _in=new_password
    )

    reload_configuration()
