#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import sh
import sys


#= Variables ==================================================================



#= Functions & objects ========================================================



#= Main program ===============================================================
if __name__ == '__main__':
    with open("/tmp/ftp_uploadedf", "a") as f:
        f.write(" ".join(sys.argv))
