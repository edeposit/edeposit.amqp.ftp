#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import os.path
from pwd import getpwnam

import settings


#= Functions & objects ========================================================
def load_users(path=settings.LOGIN_FILE):
    """
    Load users defined passwd-like format file.

    Args:
        path (str, default settings.LOGIN_FILE): path of the file,
            which will be loaded (default :attr:`.LOGIN_FILE`).

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
            settings.LOGIN_FILE,
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


def save_users(users, path=settings.LOGIN_FILE):
    """
    Save dictionary with user data to passwd-like file.

    Args:
        users (dict): dictionary with user data. For details look at dict
                      returned from :func:`load_users`.
        path (str, default settings.LOGIN_FILE): path of the file,
            which will be loaded (default :attr:`.LOGIN_FILE`).
    """
    with open(path, "w") as fh:
        for username, data in users.items():
            pass_line = username + ":" + ":".join([
                data["pass_hash"],
                data["uid"],
                data["gid"],
                data["full_name"],
                data["home"],
                data["shell"]
            ])

            fh.write(pass_line + "\n")


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
