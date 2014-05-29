#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
"""
ProFTPD_ wrapped used to manage users of the FTP server.

This module controls the ``ftpd.passwd`` (:attr:`LOGIN_FILE
<ftp.settings.LOGIN_FILE>`), creates/removes users directory and so on.

.. _ftpasswd: http://www.proftpd.org/docs/contrib/ftpasswd.html
.. _ProFTPD: http://www.proftpd.org

Warning:
    This API supposes, that it has permissions to read/write to `ProFTPD`
    configuration directory and to `root` directory for users.

Note:
    You don't have to set the permissions and everything manually, there is
    script called :mod:`.initializer`, which can do it for you automatically.
"""
import re
import os
import os.path
import shutil
from functools import wraps

import sh

import settings
import passwd_reader


# Functions & objects =========================================================
def require_root(fn):
    """
    Decorator to make sure, that user is root.
    """
    @wraps(fn)
    def xex(*args, **kwargs):
        assert os.geteuid() == 0, \
            "You have to be root to run function '%s'." % fn.__name__
        return fn(*args, **kwargs)

    return xex


@require_root
def reload_configuration():
    """
    Send signal to the proftpd daemon to reload configuration.
    """
    sh.killall("-HUP", "proftpd", _ok_code=[0, 1])


def recursive_chmod(path, mode=0755):
    """
    Recursively change ``mode`` for given ``path``. Same as ``chmod -R mode``.

    Args:
        path (str): Path of the directory/file.
        mode (octal int, default 0755): New mode of the file.

    Warning:
        Don't forget to add ``0`` at the beginning of the numbers of `mode`, or
        `Unspeakable hOrRoRs` will be awaken from their unholy sleep outside of
        the reality and they WILL eat your soul (and your files).
    """
    passwd_reader.set_permissions(path, mode=mode)
    if os.path.isfile(path):
        return

    # recursively change mode of all subdirectories
    for root, dirs, files in os.walk(path):
        for fn in files + dirs:
            passwd_reader.set_permissions(os.path.join(root, fn), mode=mode)


def _is_valid_username(username):
    """
    Check if username consist from characters "a-zA-Z0-9._-".

    Args:
        username (str): User's name.
    """
    return re.search(r"^[a-zA-Z0-9\.\_\-]*$", username)


def create_lock_file(path):
    """
    Create lock file filled with :attr:`LOCK_FILE_CONTENT
    <ftp.settings.LOCK_FILE_CONTENT>`.

    Args:
        path (str): Path to the lock file. Made from users home directory and
                    :attr:`LOCK_FILENAME <ftp.settings.LOCK_FILENAME>`.
    """
    with open(path, "w") as f:
        f.write(settings.LOCK_FILE_CONTENT)

    passwd_reader.set_permissions(path, gid=settings.PROFTPD_USERS_GID)


@require_root
def add_user(username, password):
    """
    Adds record to passwd-like file for ProFTPD, creates home directory and
    sets permissions for important files.

    Args:
        username (str): User's name.
        password (str): User's password.
    """
    assert _is_valid_username(username), \
            "Invalid format of username '%s'!" % username

    assert username not in passwd_reader.load_users(), \
            "User '%s' is already registered!" % username

    assert password, "Password is reqired!"

    # add new user to the proftpd's passwd file
    home_dir = settings.DATA_PATH + username
    sh.ftpasswd(
        passwd=True,                    # passwd file, not group file
        name=username,
        home=home_dir,                  # chroot in DATA_PATH
        shell="/bin/false",
        uid=settings.PROFTPD_USERS_GID, # TODO: parse dynamically?
        gid=settings.PROFTPD_USERS_GID,
        stdin=True,                 # tell ftpasswd to read password from stdin
        file=settings.LOGIN_FILE,
        _in=password
    )

    # create home dir if not exists
    if not os.path.exists(home_dir):
        os.makedirs(home_dir, 0775)

    # I am using PROFTPD_USERS_GID (2000) for all our users - this GID
    # shouldn't be used by other than FTP users!
    passwd_reader.set_permissions(home_dir, gid=settings.PROFTPD_USERS_GID)
    passwd_reader.set_permissions(settings.LOGIN_FILE, mode=0600)

    create_lock_file(home_dir + "/" + settings.LOCK_FILENAME)

    reload_configuration()


@require_root
def remove_user(username):
    """
    Remove user, his home directory and so on..

    Args:
        username (str): User's name.
    """
    users = passwd_reader.load_users()

    assert username in users, "Username '%s' not found!" % username

    # remove user from passwd file
    del users[username]
    passwd_reader.save_users(users)

    # remove home directory
    home_dir = settings.DATA_PATH + username
    if os.path.exists(home_dir):
        shutil.rmtree(home_dir)

    reload_configuration()


@require_root
def change_password(username, new_password):
    """
    Change password for given `username`.

    Args:
        username (str): User's name.
        new_password (str): User's new password.
    """
    assert username in passwd_reader.load_users(),\
           "Username '%s' not found!" % username

    sh.ftpasswd(
        "--change-password",
        passwd=True,        # passwd file, not group file
        name=username,
        stdin=True,         # tell ftpasswd to read password from stdin
        file=settings.LOGIN_FILE,
        _in=new_password
    )

    reload_configuration()


@require_root
def list_users():
    """
    List all registered users, which are stored in
    :attr:`LOGIN_FILE <ftp.settings.LOGIN_FILE>`.

    Returns:
        list: of str usernames.
    """
    return map(lambda (key, val): key, passwd_reader.load_users().items())
