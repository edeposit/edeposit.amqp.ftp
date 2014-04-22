#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
ProFTPD manager used to add/remove users to the FTP server.
"""
import sh


#= Variables ==================================================================



#= Functions & objects ========================================================
def is_valid_username(username):  # TODO: implement username validation
    return True


def add_user(username):
    assert is_valid_username(username), "Invalid username '%s'!" % (username,)


def remove_user(username):
    pass


#= Main program ===============================================================
if __name__ == '__main__':  # TODO: debug only, remove later
    add_user("testovaci_uzivatel")
