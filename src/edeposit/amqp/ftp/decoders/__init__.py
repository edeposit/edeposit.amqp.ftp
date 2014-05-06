#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================



#= Variables ==================================================================
SUPPORTED_FILES = [
    "csv",
    "json",
    "xml",
    "yaml"
]


#= Functions & objects ========================================================
class MetaParsingException(UserWarning):
    """docstring for MetaParsingException"""
    def __init__(self, value):
        super(MetaParsingException, self).__init__(value)
        self.value = value


def parse_meta(data):
    return "parsed data"


#= Main program ===============================================================
if __name__ == '__main__':
    pass
