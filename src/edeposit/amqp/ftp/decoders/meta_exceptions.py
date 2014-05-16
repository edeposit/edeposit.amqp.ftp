#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7


#= Functions & objects ========================================================
class MetaParsingException(UserWarning):
    """docstring for MetaParsingException"""
    def __init__(self, message):
        super(MetaParsingException, self).__init__(message)
