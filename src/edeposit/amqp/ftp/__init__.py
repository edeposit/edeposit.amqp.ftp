
#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import sys


import sh


#= Variables ==================================================================
from settings import *


#= Functions & objects ========================================================
def reload_configuration():
    sh.killall("-HUP", "proftpd")
