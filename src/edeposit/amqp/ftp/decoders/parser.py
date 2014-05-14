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

ITERABLE_TYPES = [
    list,
    tuple
]


#= Functions & objects ========================================================
def _all_correct_list(array):
    if type(array) not in ITERABLE_TYPES:
        return False

    for item in array:
        if not type(item) in ITERABLE_TYPES:
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
        except MetaParsingException:
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

    return data


def assert_exc(data, fn, exc=MetaParsingException):
    try:
        if data:
            fn(data)
        else:
            fn()
        raise AssertionError(
            "%s() fails to recognize bad data: %s" % (fn.__name__, str(data))
        )
    except exc:
        pass


def test__all_correct_list():
    assert _all_correct_list([])
    assert _all_correct_list([[1, 2], [1, 2], [1, 2]])
    assert not _all_correct_list(1)
    assert not _all_correct_list([[1], [1]])
    assert not _all_correct_list([1, [1, 2]])
    assert not _all_correct_list([[]])


def test_convert_to_dict():
    assert convert_to_dict([1, 2]) == {1: 2}
    assert convert_to_dict({1: 2}) == {1: 2}

    assert_exc([[1, 2], 2, 3], convert_to_dict, TypeError)
    assert_exc(bool, convert_to_dict)


def test_check_structure():
    assert check_structure([1, 2, 3, 4]) == {1: 2, 3: 4}
    assert check_structure({1: 2, 3: 4}) == {1: 2, 3: 4}

    assert_exc(bool, check_structure)
    assert_exc([1, 2, [3], 4], check_structure)
    assert_exc([1, 2, {}, 4], check_structure)
    assert_exc([1, 2, {}, {}], check_structure)
    assert_exc({True: {}, 3: 4}, check_structure)
