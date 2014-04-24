
#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from collections import namedtuple

import sh


#= Variables ==================================================================
from settings import *


#= Functions & objects ========================================================
def reload_configuration():
    sh.killall("-HUP", "proftpd", _ok_code=[0, 1])


class CreateUser(namedtuple("CreateUser", ["username", "password"])):
    pass


class RemoveUser(namedtuple("RemoveUser", ["username", "password"])):
    pass


class ChangePassword(namedtuple("ChangePassword", ["username", "password"])):
    pass


class ListRegisteredUsers(namedtuple("ListRegisteredUsers", [])):
    pass
