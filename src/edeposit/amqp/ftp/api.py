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


#= Functions & objects ========================================================
def require_root(fn):
    def xex(*args, **kwargs):
        assert os.geteuid() == 0, "You have to be root to run this tests."
        return fn(*args, **kwargs)

    return xex


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


def set_permissions(filename, uid=None, gid=None, mode=0775):
    """
    Set pemissions for given `filename`.

    Args:
        filename (str): name of the file/directory
        uid (int, default proftpd): user ID - if not set, user ID of `proftpd`
                                    is used
        gid (int): group ID, if not set, it is not changed
        mode (int, default 0775): unix access mode
    """
    if uid is None:
        uid = getpwnam('proftpd').pw_uid

    if gid is None:
        gid = -1

    os.chown(filename, uid, gid)
    os.chmod(filename, mode)


def create_lock_file(path):
    with open(path, "wt") as f:
        f.write(PROFTPD_LOCK_FILE_CONTENT)

    set_permissions(path, gid=PROFTPD_USER_GID)


@require_root
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

    assert password, "Password is reqired!"

    # add new user to the proftpd's passwd file
    home_dir = DATA_PATH + username
    sh.ftpasswd(
        passwd=True,        # passwd file, not group file
        name=username,
        home=home_dir,      # chroot in DATA_PATH
        shell="/bin/false",
        uid=PROFTPD_USER_GID,         # TODO: parse dynamically?
        gid=PROFTPD_USER_GID,
        stdin=True,         # tell ftpasswd to read password from stdin
        file=PROFTPD_LOGIN_FILE,
        _in=password
    )

    # create home dir if not exists
    if not os.path.exists(home_dir):
        os.makedirs(home_dir, 0775)

    # I am using PROFTPD_USER_GID (2000) for all our users - this GID shouldn't
    # be used by other than FTP users!
    set_permissions(home_dir, gid=PROFTPD_USER_GID)
    set_permissions(PROFTPD_LOGIN_FILE, mode=0600)

    create_lock_file(home_dir + "/" + PROFTPD_LOCK_FILENAME)

    reload_configuration()


@require_root
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
    home_dir = DATA_PATH + username
    if os.path.exists(home_dir):
        shutil.rmtree(home_dir)

    reload_configuration()


@require_root
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


@require_root
def list_users():
    """
    Returns:
        list: of str usernames.
    """
    return map(lambda (key, val): key, _load_users().items())
