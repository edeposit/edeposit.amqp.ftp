#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7


#= Functions & objects ========================================================
class MetaParsingException(UserWarning):
    """docstring for MetaParsingException"""
    def __init__(self, value):
        super(MetaParsingException, self).__init__(value)
        self.value = value
