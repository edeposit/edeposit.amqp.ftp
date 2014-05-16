#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import random
import string
import os.path

import edeposit.amqp.ftp as ftp
import edeposit.amqp.ftp.api as api
import edeposit.amqp.ftp.monitor as monitor
import edeposit.amqp.ftp.initializer as initializer


#= Variables ==================================================================
BASE_PATH = os.path.dirname(__file__)


#= Functions & objects ========================================================
class Inspector(object):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def call(self, fn, *args, **kwargs):
        return fn(*args, **kwargs)

    def get_random_name(self, size=8):
        out = ""
        s = string.ascii_lowercase
        for i in range(size):
            out += s[random.randint(0, len(s)-1)]

        return out
