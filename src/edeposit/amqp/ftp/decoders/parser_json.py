#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import json

import parser
from meta_exceptions import MetaParsingException


#= Functions & objects ========================================================
def decode(data):
    decoded = None
    try:
        decoded = json.loads(data)
    except Exception, e:
        raise MetaParsingException("Can't parse your JSON data: %s" % e.message)

    decoded = parser.check_structure(decoded)

    return decoded


def test_decoder():
    def test_assertions(test_str):
        data = decode(test_str)
        assert data["isbn"] == "80-86056-31-7"
        assert data["vazba"] == u"pevná"

    # dict
    test_str = """
    {
        "isbn": "80-86056-31-7",
        "vazba": "pevná"
    }
    """
    test_assertions(test_str)

    # array
    test_str = """
    [
        "isbn", "80-86056-31-7",
        "vazba", "pevná"
    ]
    """
    test_assertions(test_str)

    try:
        decode('[["isbn"], "80-86056-31-7", "asd"]')
        raise AssertionError("Field check failed!")
    except MetaParsingException:
        pass
