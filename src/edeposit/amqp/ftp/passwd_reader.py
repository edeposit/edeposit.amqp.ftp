#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
API for reading/writing of the passwd file used by ProFTPD (and also unix).

API
---
"""
# Imports =====================================================================
import os
import os.path
from pwd import getpwnam

import settings


# Functions & objects =========================================================
def load_users(path=settings.LOGIN_FILE):
    """
    Read passwd file and return dict with users and all their settings.

    Args:
        path (str, default settings.LOGIN_FILE): path of the file,
            which will be loaded (default :attr:`ftp.settings.LOGIN_FILE`).

    Returns:
        (dict): username: {pass_hash, uid, gid, full_name, home, shell}

    Example of returned data::

        {
            "xex": {
                "pass_hash": "$asd$aiosjdaiosjdásghwasdjo",
                "uid": "2000",
                "gid": "2000",
                "full_name": "ftftf",
                "home": "/home/ftp/xex",
                "shell": "/bin/false"
            }
        }
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
            path,
            cnt
        )

        users[line[0]] = {
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
    Save dictionary with user data to passwd file (default
    :attr:`ftp.settings.LOGIN_FILE`).

    Args:
        users (dict): dictionary with user data. For details look at dict
                      returned from :func:`load_users`.
        path (str, default settings.LOGIN_FILE): path of the file, where the
             data will be stored (default :attr:`ftp.settings.LOGIN_FILE`).
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


def get_ftp_uid():
    """
    Returns:
        int: UID of the proftpd/ftp user.

    Raises:
        KeyError: When ``proftpd`` and ``ftp`` user is not found.
    """
    try:
        return getpwnam('proftpd').pw_uid
    except KeyError:
        return getpwnam('ftp').pw_uid


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
        uid = get_ftp_uid()

    if gid is None:
        gid = -1

    os.chown(filename, uid, gid)
    os.chmod(filename, mode)


def _decode_config(conf_str):
    """
    Decode string to configuration dict.

    Only values defined in settings._ALLOWED_MERGES can be redefined.
    """
    conf_str = conf_str.strip()

    # convert "tttff" -> [True, True, True, False, False]
    conf = map(
        lambda x: True if x.upper() == "T" else False,
        list(conf_str)
    )

    return dict(zip(settings._ALLOWED_MERGES, conf))


def _encode_config(conf_dict):
    """Encode `conf_dict` to string."""
    out = []

    # get variables in order defined in settings._ALLOWED_MERGES
    for var in settings._ALLOWED_MERGES:
        out.append(conf_dict[var])

    # convert bools to chars
    out = map(
        lambda x: "t" if x else "f",
        out
    )

    return "".join(out)


def read_user_config(username, path=settings.LOGIN_FILE):
    """
    Read user's configuration from otherwise unused field ``full_name`` in
    passwd file.

    Configuration is stored in string as list of t/f characters.
    """
    return _decode_config(load_users(path=path)[username]["full_name"])


def save_user_config(username, conf_dict, path=settings.LOGIN_FILE):
    """
    Save user's configuration to otherwise unused field ``full_name`` in passwd
    file.
    """
    users = load_users(path=path)
    users[username]["full_name"] = _encode_config(conf_dict)
    save_users(users, path=path)
