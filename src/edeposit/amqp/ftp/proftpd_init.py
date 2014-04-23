#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import os.path
import sys
from pwd import getpwnam

from settings import *
from __init__ import reload_configuration


#= Variables ==================================================================


#= Functions & objects ========================================================,
def add_or_update(data, item, value):
    """
    Add or update value in configuration file format used by proftpd.

    Args:
        data (str): Configuration file as string.
        item (str): What option will be added/updated.
        value (str): Value of option.

    Returns:
        (string): updated configuration
    """
    data = data.splitlines()

    # to list of bytearrays (this is useful, because their reference passed to
    # other functions can be changed, and it will change objects in arrays
    # unlike strings)
    data = map(lambda x: bytearray(x), data)

    # search for the item in raw (ucommented) values
    conf = filter(lambda x: x.strip() and x.strip().split()[0] == item, data)

    if conf:
        conf[0][:] = conf[0].strip().split()[0] + " " + value
    else:
        # search for the item in commented values
        comments = filter(
            lambda x: x.strip().startswith("#") and
                    len(x.split("#")) >= 2 and
                    x.split("#")[1].split() and
                    x.split("#")[1].split()[0] == item,
            data
        )

        if comments:
            comments[0][:] = comments[0].split("#")[1].split()[0] + " " + value
        else:
            # add item, if not found in raw/commented values
            data.append(item + " " + value)

    return "\n".join(map(lambda x: str(x), data))  # convert back to string


#= Main program ===============================================================
if __name__ == '__main__':
    if os.geteuid() != 0:
        sys.stderr.write("You have to be root (uid 0) to use this program.\n")
        sys.exit(1)

    if not os.path.exists(PROFTPD_CONF_PATH):
        pass  # TODO: create/unpack default configuration

    # create data directory, where the user informations will be stored
    if not os.path.exists(PROFTPD_DATA_DIRECTORY):
        os.makedirs(PROFTPD_DATA_DIRECTORY, 0777)

    # TODO: check important files (proftpd.conf)

    # create user files if they doesn't exists
    login_file = PROFTPD_CONF_PATH + PROFTPD_LOGIN_FILE
    if not os.path.exists(login_file):
        open(login_file, "a").close()

    os.chown(login_file, getpwnam('proftpd').pw_uid, -1)
    os.chmod(login_file, 0400)

    # change important configuration values in protpd conf
    data = ""
    with open(PROFTPD_CONF_PATH + PROFTPD_CONF_FILE) as f:
        data = f.read()

    # set user file
    data = add_or_update(
        data,
        "AuthUserFile",
        PROFTPD_CONF_PATH + PROFTPD_LOGIN_FILE
    )

    data = add_or_update(data, "RequireValidShell", "off")
    data = add_or_update(data, "DefaultRoot", "~")

    with open(PROFTPD_CONF_PATH + PROFTPD_CONF_FILE, "wt") as f:
        f.write(data)

    reload_configuration()
