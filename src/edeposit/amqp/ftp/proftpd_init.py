#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import os.path
import sys

import sh

from settings import *
from __init__ import reload_configuration


#= Variables ==================================================================


#= Functions & objects ========================================================,
def add_or_update(data, item, value):
    data = data.splitlines()

    # to list of bytearrays (this is useful, because their reference passed to
    # other functions can be changed, and it will change objects in arrays
    # unlike strings)
    data = map(lambda x: bytearray(x), data)

    # search for the item in raw (ucommented) values
    

    # search for the item in commented values
    

    # add item, if not found in raw/commented values

    return "\n".join(map(lambda x: str(x), data))  # convert back to string

#= Main program ===============================================================
if __name__ == '__main__':
    if os.geteuid() != 0:
        sys.stderr.write("You have to be root to use this program.\n")
        sys.exit(1)

    if not os.path.exists(PROFTPD_CONF_PATH):
        pass  # TODO: create/unpack default configuration

    # TODO: check important files (proftpd.conf)

    # create user files if they doesn't exists
    if not os.path.exists(PROFTPD_CONF_PATH + PROFTPD_LOGIN_FILE):
        open(PROFTPD_CONF_PATH + PROFTPD_LOGIN_FILE, "a").close()
    if not os.path.exists(PROFTPD_CONF_PATH + PROFTPD_GROUP_FILE):
        open(PROFTPD_CONF_PATH + PROFTPD_GROUP_FILE, "a").close()

    data = ""
    with open(PROFTPD_CONF_PATH + PROFTPD_CONF_FILE) as f:
        data = f.read()

    data = add_or_update(data, "", "")

    # reload_configuration()  # TODO: uncomment



