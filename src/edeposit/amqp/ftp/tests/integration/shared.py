#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import random
import string


#= Variables ==================================================================
def get_random_str(size=8):
    out = ""
    s = string.ascii_lowercase
    for i in range(size):
        out += s[random.randint(0, len(s)-1)]
    return out


def is_root():
    assert os.geteuid() == 0, "You have to be root to run this tests."
