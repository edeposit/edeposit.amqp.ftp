#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module is containing all necessary global variables for package.

Module also has ability to read user-defined data from two paths:
$HOME/:attr:`_SETTINGS_PATH` and /etc/:attr:`_SETTINGS_PATH`.

Note:
    If the first path is found, other is ignored.

Example of the configuration file (``$HOME/edeposit/ftp.json``)::

    {
        "PROFTPD_CONF_PATH": "/home/bystrousak/.ftpdconf/"
    }

Attributes
----------
"""
import json
import os
import os.path


#= module configuration =======================================================
#: Module's path.
BASE_PATH = (os.path.dirname(__file__))

#: proftpd configuration directory
PROFTPD_CONF_PATH = "/etc/proftpd/"
#: proftpd configuration file (in conf. directory)
PROFTPD_CONF_FILE = "proftpd.conf"

#: file where the login informations will be stored
PROFTPD_LOGIN_FILE = "ftpd.passwd"
#: file where the group informations will be stored
PROFTPD_GROUP_FILE = "ftpd.group"


#= user configuration reader ==================================================
_ALLOWED = [str, int, float]

_SETTINGS_PATH = "/edeposit/ftp.json"
"""
Path which is appended to default search paths (``$HOME`` and ``/etc``).

Note:
    It has to start with ``/``. Variable is **appended** to the default search
    paths, so this doesn't mean, that the path is absolute!
"""


def get_all_constants():
    """
    Get list of all uppercase, non-private globals (doesn't start with ``_``).

    Returns:
        list: Uppercase names defined in `globals()` (variables from this \
              module).
    """
    return filter(
        lambda key: key.upper() == key and type(globals()[key]) in _ALLOWED,

        filter(                               # filter _PRIVATE variables
            lambda x: not x.startswith("_"),
            globals()
        )
    )


def substitute_globals(config_dict):
    """
    Set global variables to values defined in `config_dict`.

    Args:
        config_dict (dict): dictionary with data, which are used to set \
                            `globals`.

    Note:
        `config_dict` have to be dictionary, or it is ignored. Also all
        variables, that are not already in globals, or are not types defined in
        :attr:`_ALLOWED` (str, int, float) or starts with ``_`` are silently
        ignored.
    """
    constants = get_all_constants()

    if type(config_dict) != dict:
        return

    for key in config_dict:
        if key in constants and type(config_dict[key]) in _ALLOWED:
            globals()[key] = config_dict[key]


# try to read data from configuration paths ($HOME/_SETTINGS_PATH,
# /etc/_SETTINGS_PATH)
if "HOME" in os.environ and os.path.exists(os.environ["HOME"] + _SETTINGS_PATH):
    with open(os.environ["HOME"] + _SETTINGS_PATH) as f:
        substitute_globals(json.loads(f.read()))
elif os.path.exists("/etc" + _SETTINGS_PATH):
    with open("/etc" + _SETTINGS_PATH) as f:
        substitute_globals(json.loads(f.read()))
