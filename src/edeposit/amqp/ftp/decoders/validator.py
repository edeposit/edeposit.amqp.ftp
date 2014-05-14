#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from meta_exceptions import MetaParsingException


#= Variables ==================================================================
ALLOWED_TYPES = [
    str,
    unicode,
    int,
    float,
    long
]


#= Functions & objects ========================================================
def check_structure(data):
    """
    Check whether the structure is flat dictionary.
    """
    if not isinstance(data, dict):
        raise MetaParsingException(
            "Data format has invalid strucure (dictionary is expected)."
        )

    for key, val in data.iteritems():
        if type(key) not in ALLOWED_TYPES:
            raise MetaParsingException(
                "Can't parse the data file - invalid type of keyword '" +
                str(key) +
                "'!"
            )
        if type(val) not in ALLOWED_TYPES:
            raise MetaParsingException(
                "Can't parse the data file - invalid type of keyword '" +
                str(key) +
                "'!"
            )
