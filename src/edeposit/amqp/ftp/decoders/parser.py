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
def _all_correct_list(array):
    for item in array:
        if not type(item) in [list, tuple]:
            return False

        if len(item) != 2:
            return False

    return True


def convert_to_dict(data):
    if isinstance(data, dict):
        return data

    if isinstance(data, list) or isinstance(data, tuple):
        if _all_correct_list(data):
            return dict(data)
        else:
            data = zip(data[::2], data[1::2])
            return dict(data)
    else:
        raise MetaParsingException(
            "Can't decode provided metadata - unknown structure."
        )


def check_structure(data):
    """
    Check whether the structure is flat dictionary.
    """
    if not isinstance(data, dict):
        try:
            data = convert_to_dict(data)
        except MetaParsingException, e:
            raise
        except:
            raise MetaParsingException(
                "Metadata format has invalid strucure (dictionary is expected)."
            )

    for key, val in data.iteritems():
        if type(key) not in ALLOWED_TYPES:
            raise MetaParsingException(
                "Can't decode the meta file - invalid type of keyword '" +
                str(key) +
                "'!"
            )
        if type(val) not in ALLOWED_TYPES:
            raise MetaParsingException(
                "Can't decode the meta file - invalid type of keyword '" +
                str(key) +
                "'!"
            )
