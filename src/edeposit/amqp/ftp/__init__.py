
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
    sh.killall("-HUP", "proftpd")


class CreateUser(namedtuple("CreateUser", ["username"])):
    pass


class RemoveUser(namedtuple("RemoveUser", ["username"])):
    pass
